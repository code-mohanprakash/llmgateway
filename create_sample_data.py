#!/usr/bin/env python3
"""
Script to create sample usage data for testing analytics
"""
import sqlite3
from datetime import datetime, timedelta
import random

def create_sample_data():
    conn = sqlite3.connect('llm_gateway.db')
    cursor = conn.cursor()
    
    # Get organization and user IDs
    cursor.execute('SELECT id FROM organizations LIMIT 1')
    org_result = cursor.fetchone()
    if not org_result:
        print("No organization found. Please create a user first.")
        return
    
    org_id = org_result[0]
    
    cursor.execute('SELECT id FROM users WHERE organization_id = ? LIMIT 1', (org_id,))
    user_result = cursor.fetchone()
    if not user_result:
        print("No user found. Please create a user first.")
        return
    
    user_id = user_result[0]
    
    # Get API key ID
    cursor.execute('SELECT id FROM api_keys LIMIT 1')
    api_key_result = cursor.fetchone()
    if not api_key_result:
        print("No API key found. Please create an API key first.")
        return
    
    api_key_id = api_key_result[0]
    
    # Sample data for the last 30 days
    providers = ['openai', 'anthropic', 'google', 'groq', 'together']
    models = {
        'openai': ['gpt-4', 'gpt-3.5-turbo', 'gpt-4o'],
        'anthropic': ['claude-3-sonnet', 'claude-3-haiku'],
        'google': ['gemini-pro', 'gemini-1.5-flash'],
        'groq': ['llama3-8b-8192', 'mixtral-8x7b-32768'],
        'together': ['llama-3-8b-chat', 'llama-3-70b-chat']
    }
    
    # Create sample usage records for the last 30 days
    for i in range(30):
        date = datetime.now() - timedelta(days=i)
        
        # Create 5-15 requests per day
        daily_requests = random.randint(5, 15)
        
        for j in range(daily_requests):
            provider = random.choice(providers)
            model = random.choice(models[provider])
            
            # Random usage metrics
            input_tokens = random.randint(100, 2000)
            output_tokens = random.randint(50, 1000)
            total_tokens = input_tokens + output_tokens
            
            # Cost calculation (rough estimates)
            cost_per_1k = {
                'openai': {'gpt-4': 0.03, 'gpt-3.5-turbo': 0.002, 'gpt-4o': 0.015},
                'anthropic': {'claude-3-sonnet': 0.015, 'claude-3-haiku': 0.00025},
                'google': {'gemini-pro': 0.0025, 'gemini-1.5-flash': 0.0006},
                'groq': {'llama3-8b-8192': 0.0002, 'mixtral-8x7b-32768': 0.0006},
                'together': {'llama-3-8b-chat': 0.0002, 'llama-3-70b-chat': 0.0008}
            }
            
            cost = (total_tokens / 1000) * cost_per_1k[provider].get(model, 0.001)
            markup = cost * 0.2  # 20% markup
            
            response_time = random.randint(500, 3000)
            success = random.random() > 0.05  # 95% success rate
            
            cursor.execute('''
                INSERT INTO usage_records (
                    id, request_id, api_key_id, organization_id, provider, model_id,
                    input_tokens, output_tokens, total_tokens, cost_usd, markup_usd,
                    response_time_ms, success, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                f"usage_{i}_{j}",
                f"req_{i}_{j}_{random.randint(1000, 9999)}",
                api_key_id,
                org_id,
                provider,
                model,
                input_tokens,
                output_tokens,
                total_tokens,
                cost,
                markup,
                response_time,
                success,
                date.isoformat(),
                date.isoformat()
            ))
    
    conn.commit()
    conn.close()
    print("Sample usage data created successfully!")
    print("You can now test the analytics dashboard.")

if __name__ == "__main__":
    create_sample_data() 