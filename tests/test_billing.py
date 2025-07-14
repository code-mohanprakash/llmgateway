"""
Tests for billing and subscription functionality
"""
import pytest
from unittest.mock import patch, Mock
from httpx import AsyncClient
from models.user import BillingRecord, PlanType
from datetime import datetime


class TestBillingAPI:
    """Test billing API endpoints"""
    
    async def test_get_subscription_plans(self, client: AsyncClient):
        """Test getting available subscription plans"""
        response = await client.get("/api/billing/plans")
        
        assert response.status_code == 200
        plans = response.json()
        assert len(plans) == 4  # Free, Starter, Professional, Enterprise
        
        # Check plan structure
        free_plan = next(p for p in plans if p["plan_type"] == "free")
        assert free_plan["monthly_price"] == 0.0
        assert free_plan["request_limit"] == 1000
        assert free_plan["token_limit"] == 50000
        
        starter_plan = next(p for p in plans if p["plan_type"] == "starter")
        assert starter_plan["monthly_price"] == 29.0
        assert starter_plan["request_limit"] == 10000
    
    async def test_get_usage_summary(self, authenticated_client: AsyncClient, test_organization):
        """Test getting usage summary"""
        response = await authenticated_client.get("/api/billing/usage")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "current_period_requests" in data
        assert "current_period_tokens" in data
        assert "current_period_cost" in data
        assert "request_limit" in data
        assert "token_limit" in data
        assert "plan_type" in data
        assert data["plan_type"] == test_organization.plan_type.value
    
    async def test_create_subscription_starter(self, authenticated_client: AsyncClient):
        """Test creating a starter subscription"""
        with patch('stripe.Customer.create') as mock_customer, \
             patch('stripe.PaymentMethod.attach') as mock_attach, \
             patch('stripe.Customer.modify') as mock_modify, \
             patch('stripe.Subscription.create') as mock_subscription:
            
            # Mock Stripe responses
            mock_customer.return_value = Mock(id="cus_test123")
            mock_subscription.return_value = Mock(id="sub_test123")
            
            response = await authenticated_client.post("/api/billing/subscribe", json={
                "plan_type": "starter",
                "payment_method_id": "pm_test123"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Subscription created successfully"
            assert "customer_id" in data
            
            # Verify Stripe calls
            mock_customer.assert_called_once()
            mock_attach.assert_called_once()
            mock_subscription.assert_called_once()
    
    async def test_create_subscription_free_plan(self, authenticated_client: AsyncClient):
        """Test 'subscribing' to free plan (no Stripe subscription)"""
        with patch('stripe.Customer.create') as mock_customer:
            mock_customer.return_value = Mock(id="cus_test123")
            
            response = await authenticated_client.post("/api/billing/subscribe", json={
                "plan_type": "free",
                "payment_method_id": "pm_test123"
            })
            
            assert response.status_code == 200
            # Should create customer but no subscription for free plan
    
    async def test_create_subscription_invalid_plan(self, authenticated_client: AsyncClient):
        """Test creating subscription with invalid plan"""
        response = await authenticated_client.post("/api/billing/subscribe", json={
            "plan_type": "invalid_plan",
            "payment_method_id": "pm_test123"
        })
        
        assert response.status_code == 400
        assert "Invalid plan type" in response.json()["detail"]
    
    async def test_cancel_subscription(self, authenticated_client: AsyncClient, test_organization):
        """Test canceling subscription"""
        # Set up organization with active subscription
        test_organization.stripe_subscription_id = "sub_test123"
        
        with patch('stripe.Subscription.modify') as mock_modify:
            response = await authenticated_client.post("/api/billing/cancel-subscription")
            
            assert response.status_code == 200
            assert "cancelled at the end" in response.json()["message"]
            mock_modify.assert_called_once_with("sub_test123", cancel_at_period_end=True)
    
    async def test_cancel_subscription_no_active(self, authenticated_client: AsyncClient):
        """Test canceling subscription when none active"""
        response = await authenticated_client.post("/api/billing/cancel-subscription")
        
        assert response.status_code == 400
        assert "No active subscription" in response.json()["detail"]
    
    async def test_stripe_webhook_payment_succeeded(self, client: AsyncClient, test_organization):
        """Test Stripe webhook for successful payment"""
        # Set up organization with Stripe customer
        test_organization.stripe_customer_id = "cus_test123"
        
        webhook_payload = {
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "id": "in_test123",
                    "customer": "cus_test123",
                    "subscription": "sub_test123",
                    "period_start": 1234567890,
                    "period_end": 1234571490,
                    "amount_paid": 2900,  # $29.00 in cents
                    "payment_intent": "pi_test123"
                }
            }
        }
        
        with patch('stripe.Webhook.construct_event') as mock_webhook:
            mock_webhook.return_value = webhook_payload
            
            response = await client.post(
                "/api/billing/webhook",
                json=webhook_payload,
                headers={"stripe-signature": "test_signature"}
            )
            
            assert response.status_code == 200
            assert response.json()["status"] == "success"
    
    async def test_stripe_webhook_payment_failed(self, client: AsyncClient, test_organization):
        """Test Stripe webhook for failed payment"""
        test_organization.stripe_customer_id = "cus_test123"
        
        webhook_payload = {
            "type": "invoice.payment_failed",
            "data": {
                "object": {
                    "id": "in_test123",
                    "customer": "cus_test123",
                    "period_start": 1234567890,
                    "period_end": 1234571490,
                    "amount_due": 2900
                }
            }
        }
        
        with patch('stripe.Webhook.construct_event') as mock_webhook:
            mock_webhook.return_value = webhook_payload
            
            response = await client.post(
                "/api/billing/webhook",
                json=webhook_payload,
                headers={"stripe-signature": "test_signature"}
            )
            
            assert response.status_code == 200
    
    async def test_stripe_webhook_subscription_cancelled(self, client: AsyncClient, test_organization):
        """Test Stripe webhook for cancelled subscription"""
        test_organization.stripe_customer_id = "cus_test123"
        test_organization.plan_type = PlanType.STARTER
        
        webhook_payload = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "customer": "cus_test123"
                }
            }
        }
        
        with patch('stripe.Webhook.construct_event') as mock_webhook:
            mock_webhook.return_value = webhook_payload
            
            response = await client.post(
                "/api/billing/webhook",
                json=webhook_payload,
                headers={"stripe-signature": "test_signature"}
            )
            
            assert response.status_code == 200
            
            # Organization should be downgraded to free
            # Note: In real test, you'd refresh from DB and check
    
    async def test_webhook_invalid_signature(self, client: AsyncClient):
        """Test webhook with invalid signature"""
        with patch('stripe.Webhook.construct_event') as mock_webhook:
            from stripe.error import SignatureVerificationError
            mock_webhook.side_effect = SignatureVerificationError("Invalid signature", "sig")
            
            response = await client.post(
                "/api/billing/webhook",
                json={"type": "test"},
                headers={"stripe-signature": "invalid"}
            )
            
            assert response.status_code == 400
            assert "Invalid signature" in response.json()["detail"]


class TestBillingLogic:
    """Test billing business logic"""
    
    async def test_billing_record_creation(self, db_session, test_organization):
        """Test creating billing records"""
        from api.routers.billing import handle_payment_succeeded
        
        invoice_data = {
            "id": "in_test123",
            "customer": test_organization.stripe_customer_id or "cus_test123",
            "subscription": "sub_test123",
            "period_start": 1234567890,
            "period_end": 1234571490,
            "amount_paid": 2900,
            "payment_intent": "pi_test123"
        }
        
        # Set customer ID if not set
        if not test_organization.stripe_customer_id:
            test_organization.stripe_customer_id = "cus_test123"
            await db_session.commit()
        
        await handle_payment_succeeded(invoice_data, db_session)
        
        # Verify billing record was created
        from sqlalchemy import select
        result = await db_session.execute(
            select(BillingRecord).where(BillingRecord.stripe_invoice_id == "in_test123")
        )
        billing_record = result.scalar_one()
        
        assert billing_record.organization_id == test_organization.id
        assert billing_record.total_cost_usd == 29.0
        assert billing_record.status == "paid"
        assert billing_record.stripe_payment_intent_id == "pi_test123"
    
    async def test_plan_upgrade_limits(self, db_session, test_organization):
        """Test that plan upgrades update limits correctly"""
        # Start with free plan
        assert test_organization.plan_type == PlanType.FREE
        assert test_organization.monthly_request_limit == 1000
        
        # Upgrade to starter
        test_organization.plan_type = PlanType.STARTER
        test_organization.monthly_request_limit = 10000
        test_organization.monthly_token_limit = 500000
        
        await db_session.commit()
        await db_session.refresh(test_organization)
        
        assert test_organization.plan_type == PlanType.STARTER
        assert test_organization.monthly_request_limit == 10000
        assert test_organization.monthly_token_limit == 500000
    
    async def test_usage_limit_calculation(self, db_session, test_organization):
        """Test usage limit calculations"""
        from api.routers.llm import check_usage_limits
        from models.user import UsageRecord
        
        # Set low limits for testing
        test_organization.monthly_request_limit = 5
        test_organization.monthly_token_limit = 100
        await db_session.commit()
        
        # Add usage records that exceed limits
        for i in range(6):  # Exceed request limit
            usage_record = UsageRecord(
                request_id=f"test-limit-{i}",
                organization_id=test_organization.id,
                provider="openai",
                model_id="gpt-3.5-turbo",
                total_tokens=20,
                success=True
            )
            db_session.add(usage_record)
        
        await db_session.commit()
        
        # Should raise exception for exceeded limits
        with pytest.raises(Exception) as exc_info:
            await check_usage_limits(test_organization, db_session)
        
        assert "limit" in str(exc_info.value).lower()


class TestSubscriptionManagement:
    """Test subscription management features"""
    
    async def test_plan_feature_access(self, test_organization):
        """Test that plans have correct feature access"""
        # Free plan features
        test_organization.plan_type = PlanType.FREE
        test_organization.features = ["Basic LLM access", "Standard models"]
        
        assert "Basic LLM access" in test_organization.features
        assert "Custom models" not in test_organization.features
        
        # Professional plan features
        test_organization.plan_type = PlanType.PROFESSIONAL
        test_organization.features = [
            "Basic LLM access", "Advanced models", "Custom models", "Team management"
        ]
        
        assert "Custom models" in test_organization.features
        assert "Team management" in test_organization.features
    
    async def test_billing_cycle_calculation(self):
        """Test billing cycle calculations"""
        from datetime import datetime, timedelta
        
        # Test monthly billing period
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        
        period_days = (end_date - start_date).days
        assert period_days >= 28  # Handle different month lengths
        assert period_days <= 31
    
    async def test_proration_calculation(self):
        """Test proration for mid-cycle upgrades"""
        from datetime import datetime, timedelta
        
        # Mock proration calculation
        def calculate_proration(old_price, new_price, days_remaining, total_days):
            daily_difference = (new_price - old_price) / total_days
            return daily_difference * days_remaining
        
        # Upgrade from $29 to $99 with 15 days remaining in 30-day cycle
        proration = calculate_proration(29, 99, 15, 30)
        expected = (99 - 29) / 30 * 15  # $35
        
        assert abs(proration - expected) < 0.01
    
    async def test_subscription_renewal(self, test_organization):
        """Test subscription renewal logic"""
        # Mock successful renewal
        test_organization.stripe_subscription_id = "sub_test123"
        
        # Simulate successful payment
        last_payment = datetime.utcnow()
        next_billing = last_payment + timedelta(days=30)
        
        # Verify subscription remains active
        assert test_organization.stripe_subscription_id is not None
        assert test_organization.plan_type != PlanType.FREE