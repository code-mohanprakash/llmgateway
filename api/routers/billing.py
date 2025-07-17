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
from auth.rbac_middleware import require_permission

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

router = APIRouter()


class PlanPricing(BaseModel):
    plan_type: str
    name: str
    monthly_price: float
    yearly_price: float
    request_limit: int
    token_limit: int
    markup_percentage: float
    features: list[str]
    limitations: list[str]


class SubscriptionCreate(BaseModel):
    plan_type: str
    payment_method_id: str
    billing_cycle: str = "monthly"  # monthly or yearly


class UsageSummary(BaseModel):
    current_period_requests: int
    current_period_tokens: int
    current_period_cost: float
    request_limit: int
    token_limit: int
    plan_type: str
    markup_percentage: float


# Updated plan configurations with markups
PLANS = {
    "free": PlanPricing(
        plan_type="free",
        name="Free",
        monthly_price=0.0,
        yearly_price=0.0,
        request_limit=1000,
        token_limit=1000,
        markup_percentage=0.0,
        features=[
            "Basic models only (Ollama)",
            "1,000 tokens per month",
            "Community support",
            "Basic analytics",
            "API access"
        ],
        limitations=[
            "No premium models",
            "No API keys",
            "No team features",
            "No priority routing",
            "No advanced analytics",
            "No email support"
        ]
    ),
    "pro": PlanPricing(
        plan_type="pro",
        name="Pro",
        monthly_price=29.0,
        yearly_price=290.0,
        request_limit=100000,
        token_limit=100000,
        markup_percentage=0.15,  # 15% markup
        features=[
            "All models (50+ providers)",
            "100,000 tokens per month",
            "API keys",
            "Priority routing",
            "Advanced analytics",
            "Email support",
            "15% platform fee"
        ],
        limitations=[
            "No team management",
            "No custom integrations",
            "No white-label options",
            "No dedicated support",
            "No SLA guarantee"
        ]
    ),
    "enterprise": PlanPricing(
        plan_type="enterprise",
        name="Enterprise",
        monthly_price=0.0,  # Custom pricing
        yearly_price=0.0,
        request_limit=0,  # Unlimited
        token_limit=0,  # Unlimited
        markup_percentage=0.10,  # 10% markup for volume
        features=[
            "Unlimited tokens",
            "All models (50+ providers)",
            "Team management",
            "Custom integrations",
            "White-label options",
            "Dedicated support",
            "SLA guarantee",
            "10% platform fee",
            "Custom billing",
            "On-premise deployment",
            "Security audit",
            "Training & onboarding"
        ],
        limitations=[]
    )
}


@router.get("/plans", response_model=list[PlanPricing])
async def get_plans():
    """Get available subscription plans"""
    return list(PLANS.values())


@router.get("/usage", response_model=UsageSummary)
@require_permission("billing.read", "billing")
async def get_usage_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current usage summary for the organization"""
    
    try:
        # Get organization
        result = await db.execute(
            select(Organization).where(Organization.id == current_user.organization_id)
        )
        organization = result.scalar_one()
        
        # Get plan markup
        plan = PLANS.get(organization.plan_type.value, PLANS["free"])
        
        # Return simplified data for now
        return {
            "current_period_requests": 0,
            "current_period_tokens": 0,
            "current_period_cost": 0.0,
            "request_limit": organization.monthly_request_limit or 1000,
            "token_limit": organization.monthly_token_limit or 50000,
            "plan_type": organization.plan_type.value if organization.plan_type else "free",
            "markup_percentage": plan.markup_percentage,
            "top_models": []
        }
    except Exception as e:
        print(f"Error in usage endpoint: {e}")
        # Return default data on error
        return {
            "current_period_requests": 0,
            "current_period_tokens": 0,
            "current_period_cost": 0.0,
            "request_limit": 1000,
            "token_limit": 50000,
            "plan_type": "free",
            "markup_percentage": 0.0,
            "top_models": []
        }


@router.get("/current-plan")
@require_permission("billing.read", "billing")
async def get_current_plan(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current subscription plan"""
    
    # Get organization
    result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    organization = result.scalar_one()
    
    return {
        "plan_id": organization.plan_type.value if organization.plan_type else "free"
    }


@router.post("/upgrade")
async def upgrade_plan(
    plan_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upgrade subscription plan"""
    
    plan_id = plan_data.get("plan_id")
    if plan_id not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan type")
    
    plan = PLANS[plan_id]
    
    # Get organization
    result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    organization = result.scalar_one()
    
    # Update organization plan (simplified for demo)
    organization.plan_type = PlanType(plan.plan_type)
    organization.monthly_request_limit = plan.request_limit
    organization.monthly_token_limit = plan.token_limit
    
    await db.commit()
    
    return {
        "message": "Plan upgraded successfully",
        "plan": plan.dict()
    }


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
            # Calculate price based on billing cycle
            if subscription_data.billing_cycle == "yearly":
                price = plan.yearly_price
                price_id = f"price_{plan.plan_type}_yearly"
            else:
                price = plan.monthly_price
                price_id = f"price_{plan.plan_type}_monthly"
            
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{"price": price_id}],
                metadata={
                    "organization_id": str(organization.id),
                    "plan_type": plan.plan_type,
                    "billing_cycle": subscription_data.billing_cycle
                }
            )
            
            organization.stripe_subscription_id = subscription.id
        
        # Update organization plan
        organization.plan_type = PlanType(plan.plan_type)
        organization.monthly_request_limit = plan.request_limit
        organization.monthly_token_limit = plan.token_limit
        organization.features = plan.features
        organization.markup_percentage = plan.markup_percentage
        
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
@require_permission("billing.read", "billing")
async def get_invoices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get billing invoices for the organization"""
    
    try:
        # Get organization
        result = await db.execute(
            select(Organization).where(Organization.id == current_user.organization_id)
        )
        organization = result.scalar_one()
        
        # Return empty array for now (no Stripe integration in demo)
        return []
        
    except Exception as e:
        print(f"Error in invoices endpoint: {e}")
        return []


@router.get("/payment-methods")
@require_permission("billing.read", "billing")
async def get_payment_methods(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get payment methods for the organization"""
    
    # Get organization
    result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    organization = result.scalar_one()
    
    if not organization.stripe_customer_id:
        return {"payment_methods": []}
    
    try:
        payment_methods = stripe.PaymentMethod.list(
            customer=organization.stripe_customer_id,
            type="card"
        )
        
        return {
            "payment_methods": [
                {
                    "id": pm.id,
                    "brand": pm.card.brand,
                    "last4": pm.card.last4,
                    "exp_month": pm.card.exp_month,
                    "exp_year": pm.card.exp_year,
                    "is_default": pm.id == organization.default_payment_method_id
                }
                for pm in payment_methods.data
            ]
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Stripe webhooks"""
    
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_webhook_secret
        )
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
    
    organization_id = invoice.metadata.get("organization_id")
    if not organization_id:
        return
    
    # Create billing record
    billing_record = BillingRecord(
        organization_id=organization_id,
        stripe_invoice_id=invoice.id,
        amount=invoice.amount_paid / 100,
        currency=invoice.currency,
        status="paid",
        period_start=datetime.fromtimestamp(invoice.period_start),
        period_end=datetime.fromtimestamp(invoice.period_end)
    )
    
    db.add(billing_record)
    await db.commit()


async def handle_payment_failed(invoice, db: AsyncSession):
    """Handle failed payment"""
    
    organization_id = invoice.metadata.get("organization_id")
    if not organization_id:
        return
    
    # Update organization status
    result = await db.execute(
        select(Organization).where(Organization.id == organization_id)
    )
    organization = result.scalar_one()
    
    organization.plan_type = PlanType.free
    organization.monthly_request_limit = PLANS["free"].request_limit
    organization.monthly_token_limit = PLANS["free"].token_limit
    
    await db.commit()


async def handle_subscription_cancelled(subscription, db: AsyncSession):
    """Handle subscription cancellation"""
    
    organization_id = subscription.metadata.get("organization_id")
    if not organization_id:
        return
    
    # Update organization to free plan
    result = await db.execute(
        select(Organization).where(Organization.id == organization_id)
    )
    organization = result.scalar_one()
    
    organization.plan_type = PlanType.free
    organization.monthly_request_limit = PLANS["free"].request_limit
    organization.monthly_token_limit = PLANS["free"].token_limit
    organization.stripe_subscription_id = None
    
    await db.commit()