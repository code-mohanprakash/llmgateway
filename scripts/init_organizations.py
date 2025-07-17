#!/usr/bin/env python3
"""
Initialize organizations and update existing users
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import get_sync_db
from models.user import Organization, User
from sqlalchemy.orm import Session
import uuid

def init_organizations():
    """Initialize organizations and update users"""
    db = next(get_sync_db())
    
    try:
        # Check if default organization exists
        default_org = db.query(Organization).filter(Organization.slug == "default").first()
        
        if not default_org:
            # Create default organization
            default_org = Organization(
                id=str(uuid.uuid4()),
                name="Default Organization",
                slug="default",
                description="Default organization for existing users",
                plan_type="FREE"
            )
            db.add(default_org)
            db.commit()
            print(f"Created default organization: {default_org.id}")
        else:
            print(f"Default organization already exists: {default_org.id}")
        
        # Update users without organization_id
        users_without_org = db.query(User).filter(User.organization_id.is_(None)).all()
        
        for user in users_without_org:
            user.organization_id = default_org.id
            print(f"Updated user {user.email} with organization_id: {default_org.id}")
        
        db.commit()
        print(f"Updated {len(users_without_org)} users with organization_id")
        
        # Verify all users have organization_id
        users_without_org = db.query(User).filter(User.organization_id.is_(None)).all()
        if users_without_org:
            print(f"Warning: {len(users_without_org)} users still without organization_id")
        else:
            print("All users now have organization_id")
            
    except Exception as e:
        print(f"Error initializing organizations: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_organizations() 