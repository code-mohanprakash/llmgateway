"""
A/B Testing Framework for Model Bridge
"""
import uuid
import random
import statistics
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel

from database.database import get_db
from models.user import User
from auth.dependencies import get_current_user
from auth.rbac_middleware import log_audit_event, check_permission
from models.rbac import ABTest, ABTestExecution, ABTestResult

router = APIRouter(prefix="/ab-testing", tags=["A/B Testing"])


class ABTestCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    test_type: str  # "model_comparison", "provider_comparison", "cost_optimization", "quality_assessment"
    variants: List[Dict[str, Any]]
    traffic_split: Dict[str, float]  # e.g., {"A": 0.5, "B": 0.5}
    duration_days: int
    success_metrics: List[str]  # e.g., ["response_time", "cost", "quality_score"]
    statistical_significance: float = 0.05


class ABTestExecutionRequest(BaseModel):
    test_id: str
    user_id: str
    input_data: Dict[str, Any]


class ABTestResultRequest(BaseModel):
    test_id: str
    variant: str
    metrics: Dict[str, Any]
    success: bool


@router.post("/tests")
async def create_ab_test(
    request: ABTestCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new A/B test"""
    try:
        # Check permission
        await check_permission(
            user=current_user,
            resource_type="ab_testing",
            action="create",
            db=db
        )
        
        # Validate traffic split
        total_split = sum(request.traffic_split.values())
        if abs(total_split - 1.0) > 0.01:
            raise HTTPException(status_code=400, detail="Traffic split must sum to 1.0")
        
        # Create A/B test
        ab_test = ABTest(
            id=str(uuid.uuid4()),
            organization_id=current_user.organization_id,
            name=request.name,
            description=request.description,
            test_type=request.test_type,
            variants=request.variants,
            traffic_split=request.traffic_split,
            duration_days=request.duration_days,
            success_metrics=request.success_metrics,
            statistical_significance=request.statistical_significance,
            status="active",
            created_by=current_user.id,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=request.duration_days)
        )
        
        db.add(ab_test)
        await db.commit()
        await db.refresh(ab_test)
        
        # Log audit event
        await log_audit_event(
            user=current_user,
            organization=current_user.organization,
            action="ab_test.create",
            resource_type="ab_test",
            resource_id=ab_test.id,
            new_values={"test_config": request.dict()},
            success=True,
            db=db
        )
        
        return {
            "success": True,
            "data": {
                "id": ab_test.id,
                "name": ab_test.name,
                "status": ab_test.status,
                "created_at": ab_test.created_at.isoformat(),
                "expires_at": ab_test.expires_at.isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tests")
async def get_ab_tests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all A/B tests for organization"""
    try:
        # Check permission
        await check_permission(
            user=current_user,
            resource_type="ab_testing",
            action="read",
            db=db
        )
        
        result = await db.execute(
            select(ABTest).where(ABTest.organization_id == current_user.organization_id)
        )
        tests = result.scalars().all()
        
        return {
            "success": True,
            "data": [
                {
                    "id": test.id,
                    "name": test.name,
                    "description": test.description,
                    "test_type": test.test_type,
                    "status": test.status,
                    "created_at": test.created_at.isoformat(),
                    "expires_at": test.expires_at.isoformat(),
                    "total_executions": len(test.executions),
                    "total_results": len(test.results)
                }
                for test in tests
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tests/{test_id}")
async def get_ab_test(
    test_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific A/B test details"""
    try:
        # Check permission
        await check_permission(
            user=current_user,
            resource_type="ab_testing",
            action="read",
            db=db
        )
        
        result = await db.execute(
            select(ABTest).where(
                ABTest.id == test_id,
                ABTest.organization_id == current_user.organization_id
            )
        )
        test = result.scalar_one_or_none()
        
        if not test:
            raise HTTPException(status_code=404, detail="A/B test not found")
        
        return {
            "success": True,
            "data": {
                "id": test.id,
                "name": test.name,
                "description": test.description,
                "test_type": test.test_type,
                "variants": test.variants,
                "traffic_split": test.traffic_split,
                "duration_days": test.duration_days,
                "success_metrics": test.success_metrics,
                "statistical_significance": test.statistical_significance,
                "status": test.status,
                "created_at": test.created_at.isoformat(),
                "expires_at": test.expires_at.isoformat(),
                "total_executions": len(test.executions),
                "total_results": len(test.results)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/execute")
async def execute_ab_test(
    request: ABTestExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Execute A/B test for a user"""
    try:
        # Get A/B test
        result = await db.execute(
            select(ABTest).where(
                ABTest.id == request.test_id,
                ABTest.organization_id == current_user.organization_id,
                ABTest.status == "active"
            )
        )
        test = result.scalar_one_or_none()
        
        if not test:
            raise HTTPException(status_code=404, detail="Active A/B test not found")
        
        # Check if test has expired
        if test.expires_at < datetime.utcnow():
            raise HTTPException(status_code=400, detail="A/B test has expired")
        
        # Determine variant based on traffic split
        variant = _assign_variant(test.traffic_split, request.user_id)
        
        # Create execution record
        execution = ABTestExecution(
            id=str(uuid.uuid4()),
            test_id=test.id,
            user_id=request.user_id,
            variant=variant,
            input_data=request.input_data,
            executed_at=datetime.utcnow()
        )
        
        db.add(execution)
        await db.commit()
        await db.refresh(execution)
        
        return {
            "success": True,
            "data": {
                "execution_id": execution.id,
                "variant": variant,
                "test_config": test.variants[variant]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/results")
async def record_ab_test_result(
    request: ABTestResultRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Record A/B test result"""
    try:
        # Get A/B test
        result = await db.execute(
            select(ABTest).where(
                ABTest.id == request.test_id,
                ABTest.organization_id == current_user.organization_id
            )
        )
        test = result.scalar_one_or_none()
        
        if not test:
            raise HTTPException(status_code=404, detail="A/B test not found")
        
        # Create result record
        test_result = ABTestResult(
            id=str(uuid.uuid4()),
            test_id=test.id,
            variant=request.variant,
            metrics=request.metrics,
            success=request.success,
            recorded_at=datetime.utcnow()
        )
        
        db.add(test_result)
        await db.commit()
        await db.refresh(test_result)
        
        return {
            "success": True,
            "data": {
                "result_id": test_result.id,
                "variant": test_result.variant,
                "success": test_result.success
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tests/{test_id}/results")
async def get_ab_test_results(
    test_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get A/B test results and analysis"""
    try:
        # Check permission
        await check_permission(
            user=current_user,
            resource_type="ab_testing",
            action="read",
            db=db
        )
        
        # Get A/B test
        result = await db.execute(
            select(ABTest).where(
                ABTest.id == test_id,
                ABTest.organization_id == current_user.organization_id
            )
        )
        test = result.scalar_one_or_none()
        
        if not test:
            raise HTTPException(status_code=404, detail="A/B test not found")
        
        # Get results for each variant
        variant_results = {}
        for variant in test.traffic_split.keys():
            result_query = await db.execute(
                select(ABTestResult).where(
                    ABTestResult.test_id == test_id,
                    ABTestResult.variant == variant
                )
            )
            results = result_query.scalars().all()
            
            if results:
                variant_results[variant] = _analyze_variant_results(results, test.success_metrics)
        
        # Perform statistical analysis
        statistical_analysis = _perform_statistical_analysis(variant_results, test.statistical_significance)
        
        # Determine winner
        winner = _determine_winner(variant_results, test.test_type)
        
        return {
            "success": True,
            "data": {
                "test_id": test_id,
                "test_name": test.name,
                "test_type": test.test_type,
                "status": test.status,
                "variant_results": variant_results,
                "statistical_analysis": statistical_analysis,
                "winner": winner,
                "total_executions": len(test.executions),
                "total_results": len(test.results)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tests/{test_id}/stop")
async def stop_ab_test(
    test_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Stop an A/B test"""
    try:
        # Check permission
        await check_permission(
            user=current_user,
            resource_type="ab_testing",
            action="update",
            db=db
        )
        
        # Get A/B test
        result = await db.execute(
            select(ABTest).where(
                ABTest.id == test_id,
                ABTest.organization_id == current_user.organization_id
            )
        )
        test = result.scalar_one_or_none()
        
        if not test:
            raise HTTPException(status_code=404, detail="A/B test not found")
        
        # Update status
        test.status = "stopped"
        test.updated_at = datetime.utcnow()
        
        await db.commit()
        
        # Log audit event
        await log_audit_event(
            user=current_user,
            organization=current_user.organization,
            action="ab_test.stop",
            resource_type="ab_test",
            resource_id=test_id,
            success=True,
            db=db
        )
        
        return {
            "success": True,
            "message": "A/B test stopped successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def _assign_variant(traffic_split: Dict[str, float], user_id: str) -> str:
    """Assign variant based on traffic split and user ID"""
    # Use user ID to ensure consistent assignment
    random.seed(hash(user_id))
    rand_val = random.random()
    
    cumulative = 0
    for variant, percentage in traffic_split.items():
        cumulative += percentage
        if rand_val <= cumulative:
            return variant
    
    # Fallback to first variant
    return list(traffic_split.keys())[0]


def _analyze_variant_results(results: List[ABTestResult], metrics: List[str]) -> Dict[str, Any]:
    """Analyze results for a specific variant"""
    if not results:
        return {}
    
    analysis = {
        "total_executions": len(results),
        "success_rate": sum(1 for r in results if r.success) / len(results),
        "metrics": {}
    }
    
    # Analyze each metric
    for metric in metrics:
        values = [r.metrics.get(metric) for r in results if r.metrics.get(metric) is not None]
        if values:
            analysis["metrics"][metric] = {
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                "min": min(values),
                "max": max(values),
                "count": len(values)
            }
    
    return analysis


def _perform_statistical_analysis(variant_results: Dict[str, Dict], significance_level: float) -> Dict[str, Any]:
    """Perform statistical significance tests"""
    analysis = {
        "significant_differences": {},
        "confidence_intervals": {},
        "p_values": {}
    }
    
    variants = list(variant_results.keys())
    if len(variants) < 2:
        return analysis
    
    # Compare each pair of variants
    for i, variant_a in enumerate(variants):
        for variant_b in variants[i+1:]:
            comparison_key = f"{variant_a}_vs_{variant_b}"
            
            # Get success rates
            success_rate_a = variant_results[variant_a].get("success_rate", 0)
            success_rate_b = variant_results[variant_b].get("success_rate", 0)
            
            # Calculate statistical significance (simplified)
            # In production, use proper statistical tests
            difference = abs(success_rate_a - success_rate_b)
            significant = difference > significance_level
            
            analysis["significant_differences"][comparison_key] = {
                "significant": significant,
                "difference": difference,
                "variant_a_rate": success_rate_a,
                "variant_b_rate": success_rate_b
            }
    
    return analysis


def _determine_winner(variant_results: Dict[str, Dict], test_type: str) -> Optional[str]:
    """Determine the winning variant based on test type"""
    if not variant_results:
        return None
    
    if test_type == "model_comparison":
        # Compare based on quality metrics
        best_variant = None
        best_score = -1
        
        for variant, results in variant_results.items():
            quality_score = results.get("metrics", {}).get("quality_score", {}).get("mean", 0)
            if quality_score > best_score:
                best_score = quality_score
                best_variant = variant
        
        return best_variant
    
    elif test_type == "cost_optimization":
        # Compare based on cost metrics
        best_variant = None
        lowest_cost = float('inf')
        
        for variant, results in variant_results.items():
            cost = results.get("metrics", {}).get("cost", {}).get("mean", float('inf'))
            if cost < lowest_cost:
                lowest_cost = cost
                best_variant = variant
        
        return best_variant
    
    elif test_type == "provider_comparison":
        # Compare based on response time and reliability
        best_variant = None
        best_score = -1
        
        for variant, results in variant_results.items():
            response_time = results.get("metrics", {}).get("response_time", {}).get("mean", float('inf'))
            success_rate = results.get("success_rate", 0)
            
            # Combined score (lower response time, higher success rate)
            score = success_rate / max(response_time, 1)
            if score > best_score:
                best_score = score
                best_variant = variant
        
        return best_variant
    
    else:
        # Default: compare success rates
        best_variant = None
        best_rate = -1
        
        for variant, results in variant_results.items():
            success_rate = results.get("success_rate", 0)
            if success_rate > best_rate:
                best_rate = success_rate
                best_variant = variant
        
        return best_variant 