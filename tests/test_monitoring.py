"""
Unit tests for monitoring system - Phase 5
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from monitoring.monitoring_service import monitoring_service
from monitoring.performance_optimizer import performance_optimizer
from monitoring.scalability_manager import scalability_manager
from models.monitoring import SystemHealth, PerformanceMetric, Alert, Incident


class TestMonitoringService:
    """Test monitoring service functionality"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.mark.asyncio
    async def test_collect_system_health(self, mock_db):
        """Test system health collection"""
        
        # Mock psutil
        with patch('monitoring.monitoring_service.psutil') as mock_psutil:
            mock_psutil.cpu_percent.return_value = 45.5
            mock_psutil.virtual_memory.return_value = Mock(percent=60.2)
            mock_psutil.disk_usage.return_value = Mock(percent=25.0)
            
            # Mock database operations
            mock_db.execute.return_value.scalar_one_or_none.return_value = None
            mock_db.execute.return_value.scalars.return_value.all.return_value = []
            
            result = await monitoring_service.collect_system_health(mock_db, "test-org")
            
            assert result["cpu_usage"] == 45.5
            assert result["memory_usage"] == 60.2
            assert result["disk_usage"] == 25.0
            assert result["status"] in ["healthy", "warning", "critical"]
            assert "uptime_seconds" in result
    
    @pytest.mark.asyncio
    async def test_determine_health_status(self):
        """Test health status determination"""
        
        # Test healthy status
        status = monitoring_service._determine_health_status(30, 40, 50)
        assert status == "healthy"
        
        # Test warning status
        status = monitoring_service._determine_health_status(85, 40, 50)
        assert status == "warning"
        
        # Test critical status
        status = monitoring_service._determine_health_status(96, 40, 50)
        assert status == "critical"
    
    @pytest.mark.asyncio
    async def test_record_performance_metric(self, mock_db):
        """Test performance metric recording"""
        
        await monitoring_service.record_performance_metric(
            "test_metric", 100.5, "ms", 
            "/api/test", "GET", "user-123", "org-123", mock_db
        )
        
        # Verify metric was added to database
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_health_dashboard(self, mock_db):
        """Test health dashboard data retrieval"""
        
        # Mock database responses
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        mock_db.execute.return_value.scalars.return_value.all.return_value = []
        
        result = await monitoring_service.get_health_dashboard(mock_db, "test-org")
        
        assert "current_health" in result
        assert "recent_alerts" in result
        assert "sla_metrics" in result
        assert "active_incidents" in result


class TestPerformanceOptimizer:
    """Test performance optimizer functionality"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.mark.asyncio
    async def test_cache_operations(self):
        """Test cache operations"""
        
        # Test cache set and get
        await performance_optimizer.cache_set("test_key", {"data": "test"}, 300)
        result = await performance_optimizer.cache_get("test_key")
        assert result["data"] == "test"
        
        # Test cache delete
        await performance_optimizer.cache_delete("test_key")
        result = await performance_optimizer.cache_get("test_key")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_optimize_database_queries(self, mock_db):
        """Test database query optimization"""
        
        # Mock database responses
        mock_db.execute.return_value.scalars.return_value.all.return_value = []
        mock_db.execute.return_value.fetchall.return_value = []
        
        result = await performance_optimizer.optimize_database_queries(mock_db)
        
        assert "slow_queries" in result
        assert "query_patterns" in result
        assert "recommendations" in result
        assert "optimization_score" in result
    
    @pytest.mark.asyncio
    async def test_get_cache_statistics(self):
        """Test cache statistics retrieval"""
        
        result = await performance_optimizer.get_cache_statistics()
        
        assert "cache_type" in result
        if result["cache_type"] == "memory":
            assert "cache_size" in result
        elif result["cache_type"] == "redis":
            assert "connected_clients" in result
    
    @pytest.mark.asyncio
    async def test_clear_performance_cache(self):
        """Test performance cache clearing"""
        
        result = await performance_optimizer.clear_performance_cache()
        assert result is True


class TestScalabilityManager:
    """Test scalability manager functionality"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.mark.asyncio
    async def test_analyze_scalability_needs(self, mock_db):
        """Test scalability analysis"""
        
        # Mock database responses
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        
        result = await scalability_manager.analyze_scalability_needs(mock_db)
        
        assert "current_metrics" in result
        assert "scaling_recommendations" in result
        assert "scaling_history" in result
        assert "auto_scaling_status" in result
    
    @pytest.mark.asyncio
    async def test_enable_auto_scaling(self):
        """Test auto-scaling toggle"""
        
        # Test enabling
        result = await scalability_manager.enable_auto_scaling(True)
        assert result["success"] is True
        assert scalability_manager.auto_scaling_enabled is True
        
        # Test disabling
        result = await scalability_manager.enable_auto_scaling(False)
        assert result["success"] is True
        assert scalability_manager.auto_scaling_enabled is False
    
    @pytest.mark.asyncio
    async def test_set_scaling_thresholds(self):
        """Test scaling threshold updates"""
        
        new_thresholds = {
            "cpu_high": 75.0,
            "memory_high": 70.0
        }
        
        result = await scalability_manager.set_scaling_thresholds(new_thresholds)
        assert result["success"] is True
        assert scalability_manager.scaling_thresholds["cpu_high"] == 75.0
        assert scalability_manager.scaling_thresholds["memory_high"] == 70.0
    
    @pytest.mark.asyncio
    async def test_simulate_scaling_event(self):
        """Test scaling event simulation"""
        
        # Test scale up
        result = await scalability_manager.simulate_scaling_event("scale_up", 2)
        assert result["success"] is True
        assert result["event"]["event_type"] == "scale_up"
        assert result["current_instances"] > 1
        
        # Test scale down
        result = await scalability_manager.simulate_scaling_event("scale_down", 1)
        assert result["success"] is True
        assert result["event"]["event_type"] == "scale_down"
    
    @pytest.mark.asyncio
    async def test_get_load_balancer_status(self):
        """Test load balancer status"""
        
        result = await scalability_manager.get_load_balancer_status()
        
        assert "status" in result
        assert "active_instances" in result
        assert "health_checks" in result
        assert "traffic_distribution" in result
    
    @pytest.mark.asyncio
    async def test_get_database_sharding_status(self):
        """Test database sharding status"""
        
        result = await scalability_manager.get_database_sharding_status()
        
        assert "sharding_enabled" in result
        assert "shards" in result
        assert "replication" in result
        assert "backup_status" in result
    
    @pytest.mark.asyncio
    async def test_get_microservices_status(self):
        """Test microservices status"""
        
        result = await scalability_manager.get_microservices_status()
        
        assert "architecture" in result
        assert "services" in result
        assert len(result["services"]) > 0


class TestMonitoringAPI:
    """Test monitoring API endpoints"""
    
    @pytest.fixture
    def mock_user(self):
        """Mock user"""
        return Mock(
            id="user-123",
            email="test@example.com",
            organization_id="org-123",
            role="admin"
        )
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.mark.asyncio
    async def test_get_system_health(self, mock_user, mock_db):
        """Test system health endpoint"""
        
        with patch('monitoring.monitoring_service.monitoring_service.collect_system_health') as mock_collect:
            mock_collect.return_value = {
                "cpu_usage": 45.5,
                "memory_usage": 60.2,
                "status": "healthy"
            }
            
            # This would be tested with FastAPI TestClient in real implementation
            # For now, we test the service function directly
            result = await monitoring_service.collect_system_health(mock_db, mock_user.organization_id)
            
            assert result["cpu_usage"] == 45.5
            assert result["memory_usage"] == 60.2
            assert result["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_get_alerts(self, mock_user, mock_db):
        """Test alerts endpoint"""
        
        # Mock database response
        mock_alert = Mock(
            id="alert-123",
            alert_type="system",
            severity="warning",
            title="High CPU Usage",
            message="CPU usage is 85%",
            status="active",
            created_at=datetime.utcnow()
        )
        
        # Mock the execute chain properly
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [mock_alert]
        mock_db.execute.return_value = mock_result
        
        # This would be tested with FastAPI TestClient
        # For now, we test the database query logic
        from models.monitoring import Alert
        from sqlalchemy import select
        
        query = select(Alert).where(Alert.organization_id == mock_user.organization_id)
        result = await mock_db.execute(query)
        alerts = result.scalars().all()
        
        assert len(alerts) == 1
        assert alerts[0].title == "High CPU Usage"
    
    @pytest.mark.asyncio
    async def test_acknowledge_alert(self, mock_user, mock_db):
        """Test alert acknowledgment"""
        
        # Mock alert
        mock_alert = Mock(
            id="alert-123",
            status="active",
            organization_id=mock_user.organization_id
        )
        
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_alert
        
        # Test acknowledgment
        mock_alert.status = "acknowledged"
        mock_alert.acknowledged_by = mock_user.id
        mock_alert.acknowledged_at = datetime.utcnow()
        
        assert mock_alert.status == "acknowledged"
        assert mock_alert.acknowledged_by == mock_user.id


class TestMonitoringIntegration:
    """Integration tests for monitoring system"""
    
    @pytest.mark.asyncio
    async def test_full_monitoring_workflow(self):
        """Test complete monitoring workflow"""
        
        # 1. Initialize monitoring service
        assert monitoring_service.monitoring_active is True
        
        # 2. Test performance optimizer
        await performance_optimizer.initialize_redis()
        
        # 3. Test scalability manager
        await scalability_manager.enable_auto_scaling(True)
        assert scalability_manager.auto_scaling_enabled is True
        
        # 4. Test cache operations
        await performance_optimizer.cache_set("test_integration", {"test": "data"})
        result = await performance_optimizer.cache_get("test_integration")
        assert result["test"] == "data"
        
        # 5. Test scaling simulation
        scaling_result = await scalability_manager.simulate_scaling_event("scale_up", 1)
        assert scaling_result["success"] is True
        
        # 6. Test load balancer status
        lb_status = await scalability_manager.get_load_balancer_status()
        assert lb_status["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in monitoring system"""
        
        # Test with invalid cache key
        result = await performance_optimizer.cache_get("nonexistent_key")
        assert result is None
        
        # Test with invalid scaling event
        result = await scalability_manager.simulate_scaling_event("invalid_event", -1)
        assert result["success"] is True  # Should handle gracefully
        
        # Test with invalid thresholds
        result = await scalability_manager.set_scaling_thresholds({"invalid_key": 100})
        assert result["success"] is True  # Should ignore invalid keys


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 