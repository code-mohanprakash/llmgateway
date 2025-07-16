import asyncio
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Test database connection
def test_db():
    conn = sqlite3.connect('llm_gateway.db')
    cursor = conn.cursor()
    
    # Check user
    cursor.execute('SELECT id, email, organization_id FROM users WHERE email = ?', ('mohanprakash462@gmail.com',))
    user = cursor.fetchone()
    print(f"User: {user}")
    
    # Check organization
    if user:
        cursor.execute('SELECT id, name, plan_type, monthly_request_limit, monthly_token_limit FROM organizations WHERE id = ?', (user[2],))
        org = cursor.fetchone()
        print(f"Organization: {org}")
    
    # Check usage records
    cursor.execute('SELECT COUNT(*) FROM usage_records')
    usage_count = cursor.fetchone()[0]
    print(f"Usage records count: {usage_count}")
    
    conn.close()

if __name__ == "__main__":
    test_db() 