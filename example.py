"""
Example usage of the LLM Gateway
"""
import asyncio
import os
from llm_gateway import EnhancedLLMGateway


async def main():
    """Example usage of the LLM Gateway"""
    print("🚀 LLM Gateway Example")
    print("=" * 50)
    
    # Initialize gateway
    gateway = EnhancedLLMGateway()
    
    # Check if we have API keys
    if not gateway.config.available_providers:
        print("❌ No API keys found!")
        print("Please set at least one API key:")
        print("  export OPENAI_API_KEY='your_key'")
        print("  export GOOGLE_API_KEY='your_key'")
        print("  export ANTHROPIC_API_KEY='your_key'")
        return
    
    print(f"✅ Found API keys for: {', '.join(gateway.config.available_providers)}")
    
    # Initialize the gateway
    success = await gateway.initialize()
    if not success:
        print("❌ Failed to initialize gateway")
        return
    
    print(f"🎯 Gateway initialized with {len(gateway.providers)} providers")
    
    # Example 1: Simple text generation
    print("\n📝 Example 1: Simple Text Generation")
    print("-" * 40)
    
    response = await gateway.generate_text(
        prompt="Explain quantum computing in one paragraph",
        model="balanced",
        complexity="medium"
    )
    
    if response.error:
        print(f"❌ Error: {response.error}")
    else:
        print(f"✅ Response from {response.provider_name}:{response.model_id}")
        print(f"💰 Cost: ${response.cost:.4f}")
        print(f"📄 Content: {response.content[:200]}...")
    
    # Example 2: Structured output
    print("\n🏗️  Example 2: Structured Output")
    print("-" * 40)
    
    schema = {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "key_benefits": {"type": "array", "items": {"type": "string"}},
            "difficulty_level": {"type": "string", "enum": ["beginner", "intermediate", "advanced"]}
        },
        "required": ["summary", "key_benefits", "difficulty_level"]
    }
    
    response = await gateway.generate_structured_output(
        prompt="Analyze the benefits of using a multi-provider LLM gateway",
        schema=schema,
        model="best"
    )
    
    if response.error:
        print(f"❌ Error: {response.error}")
    else:
        print(f"✅ Response from {response.provider_name}:{response.model_id}")
        print(f"💰 Cost: ${response.cost:.4f}")
        print(f"📊 Structured Data: {response.content}")
    
    # Example 3: Cost optimization
    print("\n💰 Example 3: Cost Optimization")
    print("-" * 40)
    
    tasks = [
        ("Simple task", "What is 2+2?", "cheapest"),
        ("Medium task", "Explain machine learning", "balanced"),
        ("Complex task", "Write a detailed business plan", "best")
    ]
    
    total_cost = 0
    for task_name, prompt, model_type in tasks:
        response = await gateway.generate_text(
            prompt=prompt,
            model=model_type,
            max_tokens=100
        )
        
        if not response.error:
            total_cost += response.cost or 0
            print(f"  {task_name}: {response.provider_name}:{response.model_id} - ${response.cost:.4f}")
        else:
            print(f"  {task_name}: ❌ Failed")
    
    print(f"\n💸 Total cost for 3 tasks: ${total_cost:.4f}")
    
    # Example 4: Performance stats
    print("\n📊 Example 4: Performance Statistics")
    print("-" * 40)
    
    stats = gateway.get_performance_stats()
    if stats:
        for model_key, model_stats in stats.items():
            print(f"  {model_key}:")
            print(f"    Requests: {model_stats['total_requests']}")
            print(f"    Success Rate: {model_stats['success_rate']:.1%}")
            print(f"    Avg Response Time: {model_stats['avg_response_time']:.2f}s")
            print(f"    Avg Cost: ${model_stats['avg_cost']:.4f}")
    else:
        print("  No performance stats available yet")
    
    # Example 5: Health check
    print("\n🏥 Example 5: Health Check")
    print("-" * 40)
    
    health = await gateway.health_check()
    print(f"  Overall Status: {health['status']}")
    print(f"  Healthy Providers: {health['healthy_providers']}/{health['total_providers']}")
    
    for provider, status in health['providers'].items():
        status_emoji = "✅" if status.get('status') == 'healthy' else "❌"
        print(f"    {status_emoji} {provider}: {status.get('status', 'unknown')}")
    
    # Example 6: Model aliases
    print("\n🏷️  Example 6: Available Model Aliases")
    print("-" * 40)
    
    aliases = gateway.get_model_aliases()
    for alias_name, models in aliases.items():
        print(f"  {alias_name}:")
        for model in models[:2]:  # Show first 2 models
            print(f"    - {model['provider']}:{model['model_id']}")
        if len(models) > 2:
            print(f"    ... and {len(models) - 2} more")
    
    print("\n✨ Example completed!")
    print("🎉 LLM Gateway is ready for your applications!")


if __name__ == "__main__":
    asyncio.run(main())