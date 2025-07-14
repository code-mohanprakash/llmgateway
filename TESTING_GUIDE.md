# LLM Gateway SaaS - Comprehensive Testing Guide

## 🧪 How to Test Everything You've Built

This guide provides step-by-step instructions to test every component of the LLM Gateway SaaS platform, from basic functionality to security and performance.

## 📋 Pre-Testing Setup

### 1. Environment Setup
```bash
# Clone and navigate to the project
cd llmgateway

# Install all dependencies
pip install -r requirements.txt -r requirements-saas.txt

# Copy environment configuration
cp env_example.txt .env

# Edit .env with your actual API keys and configuration
nano .env
```

### 2. Required Services
```bash
# Start all services with Docker Compose
docker-compose up -d

# Verify services are running
docker-compose ps

# Check service health
curl http://localhost:8000/health
curl http://localhost:6379  # Redis
curl http://localhost:5432  # PostgreSQL (if accessible)
```

### 3. Database Setup
```bash
# Install Alembic if not already installed
pip install alembic

# Run database migrations
alembic upgrade head

# Verify tables were created
# (Check your PostgreSQL database)
```

---

## 🏗️ Testing Levels

## Level 1: Unit Tests

### Run All Tests
```bash
# Run the complete test suite
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=. --cov-report=html

# Run specific test categories
pytest tests/test_auth.py -v          # Authentication tests
pytest tests/test_llm.py -v           # Core LLM functionality
pytest tests/test_billing.py -v       # Billing and subscriptions
pytest tests/test_security.py -v      # Security and cybersecurity
```

### Test Output Interpretation
```bash
# ✅ All tests should pass
# Example good output:
========================= test session starts =========================
tests/test_auth.py::TestUserRegistration::test_register_new_user PASSED
tests/test_auth.py::TestUserLogin::test_login_valid_credentials PASSED
tests/test_llm.py::TestLLMAPIEndpoints::test_generate_text_success PASSED
========================= 50 passed in 45.2s =========================

# ❌ If tests fail, check:
# - Database connection
# - Redis connection  
# - Missing environment variables
# - Missing LLM provider API keys
```

## Level 2: API Integration Testing

### 1. Test User Registration & Authentication
```bash
# Test user registration
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "full_name": "Test User",
    "password": "securepassword123",
    "organization_name": "Test Organization"
  }'

# Expected: 200 OK with access_token and refresh_token
```

### 2. Test Login
```bash
# Test user login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=securepassword123"

# Save the access_token for subsequent requests
TOKEN="your_access_token_here"
```

### 3. Test API Key Management
```bash
# Create API key
curl -X POST http://localhost:8000/api/auth/api-keys \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test API Key",
    "scopes": ["llm:generate"],
    "rate_limit_per_minute": 60
  }'

# Save the API key for LLM requests
API_KEY="llm_your_api_key_here"
```

### 4. Test LLM Generation
```bash
# Test text generation
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing in simple terms",
    "model": "balanced",
    "max_tokens": 100
  }'

# Expected: 200 OK with generated content, model info, and cost
```

### 5. Test Structured Output
```bash
# Test JSON generation
curl -X POST http://localhost:8000/api/v1/generate-structured \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Analyze the sentiment of: I love this product!",
    "model": "best",
    "schema": {
      "type": "object",
      "properties": {
        "sentiment": {"type": "string"},
        "confidence": {"type": "number"}
      },
      "required": ["sentiment", "confidence"]
    }
  }'

# Expected: Valid JSON matching the schema
```

## Level 3: Dashboard Testing

### 1. Access Web Dashboard
```bash
# Open browser and navigate to:
http://localhost:8000

# Test login with your credentials
# Navigate through all dashboard sections:
# - Dashboard (analytics)
# - API Keys management
# - Billing & usage
# - Settings
```

### 2. Test Dashboard APIs
```bash
# Get analytics data
curl -X GET http://localhost:8000/api/dashboard/analytics \
  -H "Authorization: Bearer $TOKEN"

# Get usage summary
curl -X GET http://localhost:8000/api/billing/usage \
  -H "Authorization: Bearer $TOKEN"

# Get organization info
curl -X GET http://localhost:8000/api/dashboard/organization \
  -H "Authorization: Bearer $TOKEN"
```

## Level 4: Billing Integration Testing

### 1. Test Subscription Plans
```bash
# Get available plans
curl -X GET http://localhost:8000/api/billing/plans

# Expected: List of 4 plans (Free, Starter, Professional, Enterprise)
```

### 2. Test Stripe Integration (if configured)
```bash
# Note: Requires valid Stripe test keys in .env

# Test subscription creation (use Stripe test payment method)
curl -X POST http://localhost:8000/api/billing/subscribe \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_type": "starter",
    "payment_method_id": "pm_card_visa"
  }'

# Expected: Subscription created successfully
```

## Level 5: Performance Testing

### 1. Load Testing with concurrent requests
```bash
# Install Apache Bench (if not installed)
# On macOS: brew install httpd
# On Ubuntu: sudo apt-get install apache2-utils

# Test concurrent LLM requests
ab -n 100 -c 10 -H "Authorization: Bearer $API_KEY" \
   -p request_body.json -T application/json \
   http://localhost:8000/api/v1/generate

# Create request_body.json:
echo '{"prompt": "Test load", "model": "balanced"}' > request_body.json

# Expected: All requests succeed with reasonable response times
```

### 2. Cache Performance Testing
```bash
# Send same request multiple times to test caching
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/v1/generate \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"prompt": "What is the capital of France?", "model": "balanced"}' \
    -w "Time: %{time_total}s\n"
done

# Expected: First request slower, subsequent requests faster (cached)
# Look for "cached": true in responses
```

## Level 6: Security Testing

### 1. Authentication Security
```bash
# Test invalid credentials
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=invalid@example.com&password=wrongpassword"

# Expected: 401 Unauthorized

# Test invalid API key
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Authorization: Bearer invalid_key" \
  -d '{"prompt": "test"}'

# Expected: 401 Unauthorized
```

### 2. Rate Limiting Testing
```bash
# Send requests rapidly to test rate limiting
for i in {1..70}; do
  curl -X POST http://localhost:8000/api/v1/generate \
    -H "Authorization: Bearer $API_KEY" \
    -d '{"prompt": "Rate limit test '$i'", "model": "balanced"}' &
done
wait

# Expected: Some requests should return 429 Too Many Requests
```

### 3. Input Validation Testing
```bash
# Test SQL injection prevention
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"prompt": "'; DROP TABLE users; --", "model": "balanced"}'

# Expected: Request handled safely, no database errors

# Test XSS prevention
curl -X POST http://localhost:8000/api/auth/register \
  -d '{
    "email": "xss@example.com",
    "full_name": "<script>alert(\"xss\")</script>",
    "password": "password123",
    "organization_name": "Test"
  }'

# Expected: Input sanitized or rejected
```

## Level 7: Monitoring & Observability Testing

### 1. Metrics Collection
```bash
# Check Prometheus metrics
curl http://localhost:8000/metrics

# Expected: Prometheus-format metrics
# Look for custom metrics like:
# - llm_gateway_requests_total
# - llm_gateway_request_duration_seconds
# - llm_gateway_tokens_total
```

### 2. Health Checks
```bash
# Application health
curl http://localhost:8000/health

# API health  
curl http://localhost:8000/api/health

# LLM Gateway health (with API key)
curl -H "Authorization: Bearer $API_KEY" \
     http://localhost:8000/api/v1/health

# Expected: All should return "healthy" status
```

### 3. Grafana Dashboards (if running)
```bash
# Access Grafana at http://localhost:3000
# Login: admin/admin
# Import dashboards for LLM Gateway metrics
```

---

## 🔍 Troubleshooting Common Issues

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose logs postgres

# Test database connection
psql postgresql://llm_gateway:password@localhost:5432/llm_gateway -c "SELECT 1;"

# Reset database if needed
docker-compose down -v
docker-compose up -d postgres
alembic upgrade head
```

### Redis Connection Issues
```bash
# Check Redis is running
docker-compose logs redis

# Test Redis connection
redis-cli -h localhost ping

# Expected: PONG
```

### LLM Provider Issues
```bash
# Check provider API keys in .env
grep "API_KEY" .env

# Test provider directly
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models

# Expected: List of available models
```

### Frontend Issues
```bash
# Build frontend (if needed)
cd web/
npm install
npm run build
cd ..

# Check static files are served
curl http://localhost:8000/static/js/main.js
```

---

## 📊 Performance Benchmarks

### Expected Performance Metrics
- **Response Time**: <2 seconds for LLM requests
- **Throughput**: 50+ requests/second with proper scaling
- **Cache Hit Rate**: 60-80% for repeated queries
- **Uptime**: 99.9% with provider failover
- **Error Rate**: <0.1% under normal conditions

### Load Testing Results to Expect
```bash
# Good performance indicators:
# - 95% of requests complete within 3 seconds
# - 0% error rate under normal load
# - Linear scaling with increased resources
# - Cache improves performance for repeated requests
```

---

## 🛡️ Security Validation Checklist

### ✅ Authentication & Authorization
- [ ] JWT tokens are secure and expire appropriately
- [ ] API keys are hashed and cannot be reverse-engineered
- [ ] Role-based access control works correctly
- [ ] Organizations are properly isolated

### ✅ Input Validation
- [ ] SQL injection attacks are prevented
- [ ] XSS attacks are mitigated
- [ ] Command injection is blocked
- [ ] Path traversal attacks fail

### ✅ Rate Limiting
- [ ] Rate limits are enforced correctly
- [ ] Rate limit bypass attempts fail
- [ ] Different rate limits work for different users

### ✅ Data Protection
- [ ] Sensitive data is not logged
- [ ] Error messages don't leak information
- [ ] Database queries are parameterized
- [ ] API responses don't expose internal details

---

## 🎯 Testing Checklist Summary

### ✅ Core Functionality
- [ ] User registration and login work
- [ ] API key creation and management function
- [ ] LLM text generation works with multiple providers
- [ ] Structured output generation works
- [ ] Model routing (fastest, cheapest, best) functions
- [ ] Provider failover works when providers are down

### ✅ SaaS Features
- [ ] Multi-tenancy isolates organizations correctly
- [ ] Billing plans and subscription management work
- [ ] Usage tracking records all API calls
- [ ] Rate limiting enforces limits correctly
- [ ] Web dashboard displays analytics properly

### ✅ Performance & Reliability
- [ ] Caching improves response times and reduces costs
- [ ] System handles concurrent requests gracefully
- [ ] Database performs well under load
- [ ] Monitoring captures all necessary metrics

### ✅ Security & Compliance
- [ ] All authentication mechanisms are secure
- [ ] Input validation prevents injection attacks
- [ ] Access control enforces proper permissions
- [ ] Sensitive data is protected throughout

---

## 🚀 Production Deployment Testing

### Pre-Production Checklist
```bash
# 1. Update environment for production
cp .env .env.production
# Edit .env.production with production values

# 2. Test with production-like data
# - Create test organizations
# - Generate realistic usage patterns
# - Test billing with Stripe test mode

# 3. Performance testing with realistic load
# - Test with expected user count
# - Verify database performance
# - Test failover scenarios

# 4. Security audit
# - Run security tests
# - Check for exposed secrets
# - Verify HTTPS configuration
# - Test firewall rules

# 5. Monitoring setup
# - Configure alerts
# - Test notification channels
# - Verify metric collection
# - Set up log aggregation
```

---

**This testing guide ensures that every component of your LLM Gateway SaaS platform works correctly, securely, and at scale. Follow this guide systematically to validate that your implementation is production-ready.**