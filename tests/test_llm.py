"""
Tests for LLM Gateway core functionality
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from httpx import AsyncClient
from models.user import UsageRecord
from llm_gateway import EnhancedLLMGateway


class TestLLMAPIEndpoints:
    """Test LLM API endpoints"""
    
    async def test_generate_text_success(self, client: AsyncClient, test_api_key):
        """Test successful text generation"""
        api_key_obj, api_key_string = test_api_key
        
        # Mock the LLM Gateway response
        with patch('api.routers.llm.gateway.generate_text') as mock_generate:
            mock_response = Mock()
            mock_response.content = "Test response content"
            mock_response.model_id = "gpt-3.5-turbo"
            mock_response.provider_name = "openai"
            mock_response.cost = 0.002
            mock_response.input_tokens = 10
            mock_response.output_tokens = 15
            mock_response.total_tokens = 25
            mock_generate.return_value = mock_response
            
            response = await client.post(
                "/api/v1/generate",
                headers={"Authorization": f"Bearer {api_key_string}"},
                json={
                    "prompt": "Test prompt",
                    "model": "balanced",
                    "max_tokens": 100
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Test response content"
        assert data["model_id"] == "gpt-3.5-turbo"
        assert data["provider_name"] == "openai"
        assert data["cost"] == 0.002
        assert "request_id" in data
    
    async def test_generate_text_with_cache(self, client: AsyncClient, test_api_key):
        """Test cached response"""
        api_key_obj, api_key_string = test_api_key
        
        # Mock cached response
        with patch('api.routers.llm.get_cached_response') as mock_cache:
            mock_cache.return_value = {
                "content": "Cached response",
                "model_id": "gpt-3.5-turbo",
                "provider_name": "openai",
                "input_tokens": 10,
                "output_tokens": 15,
                "total_tokens": 25,
                "cost": 0.002
            }
            
            response = await client.post(
                "/api/v1/generate",
                headers={"Authorization": f"Bearer {api_key_string}"},
                json={
                    "prompt": "Test prompt",
                    "model": "balanced"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Cached response"
        assert data["cached"] == True
        assert data["cost"] == 0.0  # Cached responses are free
    
    async def test_generate_structured_output(self, client: AsyncClient, test_api_key):
        """Test structured output generation"""
        api_key_obj, api_key_string = test_api_key
        
        schema = {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "score": {"type": "number"}
            },
            "required": ["summary", "score"]
        }
        
        with patch('api.routers.llm.gateway.generate_structured_output') as mock_generate:
            mock_response = Mock()
            mock_response.content = '{"summary": "Test summary", "score": 8.5}'
            mock_response.model_id = "gpt-4"
            mock_response.provider_name = "openai"
            mock_response.cost = 0.03
            mock_response.input_tokens = 20
            mock_response.output_tokens = 10
            mock_response.total_tokens = 30
            mock_generate.return_value = mock_response
            
            response = await client.post(
                "/api/v1/generate-structured",
                headers={"Authorization": f"Bearer {api_key_string}"},
                json={
                    "prompt": "Analyze this text",
                    "schema": schema,
                    "model": "best"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert '"summary"' in data["content"]
        assert '"score"' in data["content"]
    
    async def test_generate_without_schema_fails(self, client: AsyncClient, test_api_key):
        """Test structured output without schema fails"""
        api_key_obj, api_key_string = test_api_key
        
        response = await client.post(
            "/api/v1/generate-structured",
            headers={"Authorization": f"Bearer {api_key_string}"},
            json={
                "prompt": "Test prompt",
                "model": "balanced"
            }
        )
        
        assert response.status_code == 400
        assert "Schema is required" in response.json()["detail"]
    
    async def test_invalid_api_key(self, client: AsyncClient):
        """Test request with invalid API key"""
        response = await client.post(
            "/api/v1/generate",
            headers={"Authorization": "Bearer invalid_key"},
            json={"prompt": "Test", "model": "balanced"}
        )
        
        assert response.status_code == 401
    
    async def test_missing_api_key(self, client: AsyncClient):
        """Test request without API key"""
        response = await client.post(
            "/api/v1/generate",
            json={"prompt": "Test", "model": "balanced"}
        )
        
        assert response.status_code == 401
    
    async def test_rate_limit_exceeded(self, client: AsyncClient, test_api_key):
        """Test rate limiting"""
        api_key_obj, api_key_string = test_api_key
        
        # Mock rate limit exceeded
        with patch('auth.dependencies.check_rate_limits') as mock_check:
            from fastapi import HTTPException
            mock_check.side_effect = HTTPException(status_code=429, detail="Rate limit exceeded")
            
            response = await client.post(
                "/api/v1/generate",
                headers={"Authorization": f"Bearer {api_key_string}"},
                json={"prompt": "Test", "model": "balanced"}
            )
        
        assert response.status_code == 429
    
    async def test_usage_limit_exceeded(self, client: AsyncClient, test_api_key, test_organization):
        """Test usage limit enforcement"""
        api_key_obj, api_key_string = test_api_key
        
        # Set very low limits
        test_organization.monthly_request_limit = 0
        
        response = await client.post(
            "/api/v1/generate",
            headers={"Authorization": f"Bearer {api_key_string}"},
            json={"prompt": "Test", "model": "balanced"}
        )
        
        assert response.status_code == 429
        assert "limit" in response.json()["detail"].lower()
    
    async def test_list_models(self, client: AsyncClient, test_api_key):
        """Test listing available models"""
        api_key_obj, api_key_string = test_api_key
        
        with patch('api.routers.llm.gateway.get_available_models') as mock_models:
            mock_models.return_value = [
                {"provider": "openai", "model_id": "gpt-3.5-turbo"},
                {"provider": "anthropic", "model_id": "claude-3-sonnet"}
            ]
            
            response = await client.get(
                "/api/v1/models",
                headers={"Authorization": f"Bearer {api_key_string}"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert len(data["models"]) == 2
    
    async def test_health_check(self, client: AsyncClient, test_api_key):
        """Test gateway health check"""
        api_key_obj, api_key_string = test_api_key
        
        with patch('api.routers.llm.gateway.health_check') as mock_health:
            mock_health.return_value = {
                "status": "healthy",
                "providers": {"openai": "healthy", "anthropic": "healthy"}
            }
            
            response = await client.get(
                "/api/v1/health",
                headers={"Authorization": f"Bearer {api_key_string}"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestLLMGatewayCore:
    """Test the core LLM Gateway functionality"""
    
    @pytest.fixture
    def gateway(self):
        """Create a test gateway instance"""
        return EnhancedLLMGateway()
    
    async def test_model_alias_resolution(self, gateway):
        """Test model alias resolution"""
        # Mock provider availability
        with patch.object(gateway, '_get_available_providers') as mock_providers:
            mock_providers.return_value = ["openai", "anthropic", "google"]
            
            # Test fastest alias
            model_config = gateway._resolve_model_alias("fastest")
            assert model_config is not None
            
            # Test cheapest alias
            model_config = gateway._resolve_model_alias("cheapest")
            assert model_config is not None
            
            # Test best alias
            model_config = gateway._resolve_model_alias("best")
            assert model_config is not None
    
    async def test_provider_fallback(self, gateway):
        """Test provider failover mechanism"""
        with patch.object(gateway, '_try_provider') as mock_try:
            # First provider fails, second succeeds
            mock_try.side_effect = [
                Exception("Provider 1 failed"),
                Mock(content="Success", provider_name="provider2")
            ]
            
            # Mock provider list
            gateway.provider_configs = ["provider1", "provider2"]
            
            result = await gateway._generate_with_fallback("test prompt", "test-model")
            assert result.content == "Success"
            assert result.provider_name == "provider2"
    
    async def test_cost_calculation(self, gateway):
        """Test cost calculation"""
        # Mock provider cost calculation
        with patch.object(gateway, '_calculate_cost') as mock_cost:
            mock_cost.return_value = 0.002
            
            cost = gateway._calculate_cost("openai", "gpt-3.5-turbo", 100, 50)
            assert cost == 0.002
            mock_cost.assert_called_once()
    
    async def test_health_check_all_providers(self, gateway):
        """Test health check across all providers"""
        with patch.object(gateway, '_check_provider_health') as mock_health:
            mock_health.return_value = True
            
            health_status = await gateway.health_check()
            assert health_status["status"] in ["healthy", "degraded"]
            assert "providers" in health_status


class TestUsageTracking:
    """Test usage tracking and billing"""
    
    async def test_usage_record_creation(self, db_session, test_api_key, test_organization):
        """Test usage record creation"""
        from api.routers.llm import record_usage
        
        api_key_obj, _ = test_api_key
        
        await record_usage(
            request_id="test-123",
            api_key=api_key_obj,
            organization=test_organization,
            provider="openai",
            model_id="gpt-3.5-turbo",
            input_tokens=100,
            output_tokens=50,
            cost=0.002,
            response_time_ms=1500,
            success=True,
            db=db_session
        )
        
        # Verify record was created
        from sqlalchemy import select
        result = await db_session.execute(
            select(UsageRecord).where(UsageRecord.request_id == "test-123")
        )
        usage_record = result.scalar_one()
        
        assert usage_record.provider == "openai"
        assert usage_record.model_id == "gpt-3.5-turbo"
        assert usage_record.input_tokens == 100
        assert usage_record.output_tokens == 50
        assert usage_record.total_tokens == 150
        assert usage_record.cost_usd == 0.002
        assert usage_record.success == True
    
    async def test_usage_aggregation(self, db_session, test_organization):
        """Test usage aggregation for billing"""
        from sqlalchemy import func, select
        
        # Create multiple usage records
        for i in range(5):
            usage_record = UsageRecord(
                request_id=f"test-{i}",
                organization_id=test_organization.id,
                provider="openai",
                model_id="gpt-3.5-turbo",
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                cost_usd=0.002,
                markup_usd=0.0004,
                success=True
            )
            db_session.add(usage_record)
        
        await db_session.commit()
        
        # Test aggregation
        result = await db_session.execute(
            select(
                func.count(UsageRecord.id).label("request_count"),
                func.sum(UsageRecord.total_tokens).label("total_tokens"),
                func.sum(UsageRecord.cost_usd + UsageRecord.markup_usd).label("total_cost")
            ).where(
                UsageRecord.organization_id == test_organization.id,
                UsageRecord.success == True
            )
        )
        
        stats = result.first()
        assert stats.request_count == 5
        assert stats.total_tokens == 750  # 5 * 150
        assert float(stats.total_cost) == 0.012  # 5 * (0.002 + 0.0004)


class TestCaching:
    """Test Redis caching functionality"""
    
    async def test_cache_key_generation(self):
        """Test cache key generation"""
        from utils.cache import RedisCache
        
        cache = RedisCache()
        key1 = cache._generate_cache_key("Hello world", "gpt-3.5-turbo", temperature=0.7)
        key2 = cache._generate_cache_key("Hello world", "gpt-3.5-turbo", temperature=0.7)
        key3 = cache._generate_cache_key("Hello world", "gpt-3.5-turbo", temperature=0.8)
        
        # Same parameters should generate same key
        assert key1 == key2
        
        # Different parameters should generate different keys
        assert key1 != key3
    
    @pytest.mark.asyncio
    async def test_cache_set_get(self):
        """Test cache set and get operations"""
        from utils.cache import cache
        
        # Mock Redis operations
        with patch.object(cache.redis_client, 'get') as mock_get, \
             patch.object(cache.redis_client, 'setex') as mock_setex:
            
            # Test cache miss
            mock_get.return_value = None
            result = await cache.get("test prompt", "gpt-3.5-turbo")
            assert result is None
            
            # Test cache set
            response_data = {
                "content": "Test response",
                "model_id": "gpt-3.5-turbo",
                "provider_name": "openai"
            }
            
            await cache.set("test prompt", "gpt-3.5-turbo", response_data)
            mock_setex.assert_called_once()
    
    async def test_cache_stats(self):
        """Test cache statistics"""
        from utils.cache import cache
        
        with patch.object(cache.redis_client, 'info') as mock_info, \
             patch.object(cache.redis_client, 'keys') as mock_keys:
            
            mock_info.return_value = {
                'used_memory_human': '1.2M',
                'keyspace_hits': 100,
                'keyspace_misses': 20
            }
            mock_keys.return_value = ['cache:key1', 'cache:key2']
            
            stats = await cache.get_cache_stats()
            assert stats['total_keys'] == 2
            assert stats['memory_used'] == '1.2M'
            assert stats['hit_rate'] == 83.33  # 100/(100+20)*100