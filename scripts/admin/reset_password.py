#!/usr/bin/env python3
"""
Password reset script for Model Bridge
"""
import sqlite3
import hashlib
import argparse

def reset_password(email, new_password, db_path='llm_gateway.db'):
    # Hash the new password using SHA256 (consistent with the app)
    hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
    
    # Update the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'UPDATE users SET hashed_password = ? WHERE email = ?',
            (hashed_password, email)
        )
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"✅ Password successfully reset for {email}")
            print(f"New password: {new_password}")
        else:
            print(f"❌ User {email} not found in database")
            
    except Exception as e:
        print(f"❌ Error resetting password: {e}")
    finally:
        conn.close()

def list_users(db_path='llm_gateway.db'):
    """List all users in the database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT email, full_name, is_active, is_verified FROM users')
        users = cursor.fetchall()
        
        if users:
            print("\n📋 Users in database:")
            for email, full_name, is_active, is_verified in users:
                status = "✅ Active" if is_active else "❌ Inactive"
                verified = "✅ Verified" if is_verified else "❌ Not verified"
                print(f"  {email} ({full_name}) - {status}, {verified}")
        else:
            print("No users found in database")
            
    except Exception as e:
        print(f"❌ Error listing users: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Reset user password')
    parser.add_argument('--email', required=True, help='User email')
    parser.add_argument('--password', required=True, help='New password')
    parser.add_argument('--db', default='llm_gateway.db', help='Database file path')
    parser.add_argument('--list-users', action='store_true', help='List all users')
    
    args = parser.parse_args()
    
    if args.list_users:
        list_users(args.db)
    else:
        reset_password(args.email, args.password, args.db) 