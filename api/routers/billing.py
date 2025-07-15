"""
Billing and subscription management with Stripe
"""
import os
import stripe
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract

from database.database import get_db
from models.user import User, Organization, BillingRecord, UsageRecord, PlanType
from auth.dependencies import get_current_user, require_role

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

router = APIRouter()


class PlanPricing(BaseModel):
    plan_type: str
    name: str
    monthly_price: float
    request_limit: int
    token_limit: int
    features: list[str]


class SubscriptionCreate(BaseModel):
    plan_type: str
    payment_method_id: str


class UsageSummary(BaseModel):
    current_period_requests: int
    current_period_tokens: int
    current_period_cost: float
    request_limit: int
    token_limit: int
    plan_type: str


# Plan configurations
PLANS = {
    "free": PlanPricing(
        plan_type="free",
        name="Free",
        monthly_price=0.0,
        request_limit=1000,
        token_limit=50000,
        features=["Basic LLM access", "Standard models", "Email support"]
    ),
    "starter": PlanPricing(
        plan_type="starter",
        name="Starter",
        monthly_price=29.0,
        request_limit=10000,
        token_limit=500000,
        features=["All Free features", "Advanced models", "Priority support", "Analytics dashboard"]
    ),
    "professional": PlanPricing(
        plan_type="professional",
        name="Professional",
        monthly_price=99.0,
        request_limit=50000,
        token_limit=2500000,
        features=["All Starter features", "Custom models", "Team management", "SLA guarantee"]
    ),
    "enterprise": PlanPricing(
        plan_type="enterprise",
        name="Enterprise",
        monthly_price=299.0,
        request_limit=200000,
        token_limit=10000000,
        features=["All Professional features", "Dedicated support", "Custom deployment", "Advanced security"]
    )
}


@router.get("/plans", response_model=list[PlanPricing])
async def get_plans():
    """Get available subscription plans"""
    return list(PLANS.values())


@router.get("/usage", response_model=UsageSummary)
async def get_usage_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current usage summary for the organization"""
    
    # Get organization
    result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    organization = result.scalar_one()
    
    # Get current month usage
    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year
    
    usage_result = await db.execute(
        select(
            func.count(UsageRecord.id).label("request_count"),
            func.sum(UsageRecord.total_tokens).label("token_count"),
            func.sum(UsageRecord.cost_usd + UsageRecord.markup_usd).label("total_cost")
        ).where(
            UsageRecord.organization_id == organization.id,
            extract('month', UsageRecord.created_at) == current_month,
            extract('year', UsageRecord.created_at) == current_year,
            UsageRecord.success == True
        )
    )
    
    usage = usage_result.first()
    
    return UsageSummary(
        current_period_requests=usage.request_count or 0,
        current_period_tokens=usage.token_count or 0,
        current_period_cost=float(usage.total_cost or 0),
        request_limit=organization.monthly_request_limit,
        token_limit=organization.monthly_token_limit,
        plan_type=organization.plan_type.value
    )


@router.post("/subscribe")
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Create or update subscription"""
    
    if subscription_data.plan_type not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan type")
    
    plan = PLANS[subscription_data.plan_type]
    
    # Get organization
    result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    organization = result.scalar_one()
    
    try:
        # Create or get Stripe customer
        if not organization.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=organization.name,
                metadata={
                    "organization_id": str(organization.id),
                    "user_id": str(current_user.id)
                }
            )
            organization.stripe_customer_id = customer.id
        else:
            customer = stripe.Customer.retrieve(organization.stripe_customer_id)
        
        # Attach payment method
        stripe.PaymentMethod.attach(
            subscription_data.payment_method_id,
            customer=customer.id
        )
        
        # Set as default payment method
        stripe.Customer.modify(
            customer.id,
            invoice_settings={
                "default_payment_method": subscription_data.payment_method_id
            }
        )
        
        # Create subscription if not free plan
        if plan.plan_type != "free":
            # Create price in Stripe (you should create these beforehand)
            price_id = f"price_{plan.plan_type}_monthly"  # Predefined price IDs
            
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{"price": price_id}],
                metadata={
                    "organization_id": str(organization.id),
                    "plan_type": plan.plan_type
                }
            )
            
            organization.stripe_subscription_id = subscription.id
        
        # Update organization plan
        organization.plan_type = PlanType(plan.plan_type)
        organization.monthly_request_limit = plan.request_limit
        organization.monthly_token_limit = plan.token_limit
        organization.features = plan.features
        
        await db.commit()
        
        return {
            "message": "Subscription created successfully",
            "plan": plan.dict(),
            "customer_id": customer.id
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cancel-subscription")
async def cancel_subscription(
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Cancel current subscription"""
    
    # Get organization
    result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    organization = result.scalar_one()
    
    if not organization.stripe_subscription_id:
        raise HTTPException(status_code=400, detail="No active subscription")
    
    try:
        # Cancel Stripe subscription
        stripe.Subscription.modify(
            organization.stripe_subscription_id,
            cancel_at_period_end=True
        )
        
        return {"message": "Subscription will be cancelled at the end of the billing period"}
        
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/invoices")
async def get_invoices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get billing invoices for the organization"""
    
    # Get organization
    result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    organization = result.scalar_one()
    
    # Get billing records
    billing_result = await db.execute(
        select(BillingRecord).where(
            BillingRecord.organization_id == organization.id
        ).order_by(
            BillingRecord.billing_period_start.desc()
        ).limit(50)
    )
    
    billing_records = billing_result.scalars().all()
    
    invoices = []
    for record in billing_records:
        invoices.append({
            "id": str(record.id),
            "invoice_number": record.stripe_invoice_id or f"INV-{record.id}",
            "amount": record.total_cost_usd,
            "status": record.status,
            "billing_period_start": record.billing_period_start.isoformat(),
            "billing_period_end": record.billing_period_end.isoformat(),
            "paid_at": record.paid_at.isoformat() if record.paid_at else None,
            "created_at": record.created_at.isoformat()
        })
    
    return invoices


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Stripe webhooks"""
    
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, stripe_webhook_secret)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    if event["type"] == "invoice.payment_succeeded":
        await handle_payment_succeeded(event["data"]["object"], db)
    elif event["type"] == "invoice.payment_failed":
        await handle_payment_failed(event["data"]["object"], db)
    elif event["type"] == "customer.subscription.deleted":
        await handle_subscription_cancelled(event["data"]["object"], db)
    
    return {"status": "success"}


async def handle_payment_succeeded(invoice, db: AsyncSession):
    """Handle successful payment"""
    
    customer_id = invoice["customer"]
    subscription_id = invoice["subscription"]
    
    # Find organization by customer ID
    result = await db.execute(
        select(Organization).where(Organization.stripe_customer_id == customer_id)
    )
    organization = result.scalar_one_or_none()
    
    if organization:
        # Create billing record
        billing_record = BillingRecord(
            organization_id=organization.id,
            billing_period_start=datetime.fromtimestamp(invoice["period_start"]),
            billing_period_end=datetime.fromtimestamp(invoice["period_end"]),
            total_cost_usd=invoice["amount_paid"] / 100,  # Convert from cents
            stripe_invoice_id=invoice["id"],
            stripe_payment_intent_id=invoice["payment_intent"],
            status="paid",
            paid_at=datetime.utcnow()
        )
        
        db.add(billing_record)
        await db.commit()


async def handle_payment_failed(invoice, db: AsyncSession):
    """Handle failed payment"""
    
    customer_id = invoice["customer"]
    
    # Find organization by customer ID
    result = await db.execute(
        select(Organization).where(Organization.stripe_customer_id == customer_id)
    )
    organization = result.scalar_one_or_none()
    
    if organization:
        # Create failed billing record
        billing_record = BillingRecord(
            organization_id=organization.id,
            billing_period_start=datetime.fromtimestamp(invoice["period_start"]),
            billing_period_end=datetime.fromtimestamp(invoice["period_end"]),
            total_cost_usd=invoice["amount_due"] / 100,
            stripe_invoice_id=invoice["id"],
            status="failed"
        )
        
        db.add(billing_record)
        
        # Optionally downgrade to free plan on payment failure
        # organization.plan_type = PlanType.FREE
        # organization.monthly_request_limit = PLANS["free"].request_limit
        # organization.monthly_token_limit = PLANS["free"].token_limit
        
        await db.commit()


async def handle_subscription_cancelled(subscription, db: AsyncSession):
    """Handle cancelled subscription"""
    
    customer_id = subscription["customer"]
    
    # Find organization by customer ID
    result = await db.execute(
        select(Organization).where(Organization.stripe_customer_id == customer_id)
    )
    organization = result.scalar_one_or_none()
    
    if organization:
        # Downgrade to free plan
        organization.plan_type = PlanType.FREE
        organization.monthly_request_limit = PLANS["free"].request_limit
        organization.monthly_token_limit = PLANS["free"].token_limit
        organization.features = PLANS["free"].features
        organization.stripe_subscription_id = None
        
        await db.commit()