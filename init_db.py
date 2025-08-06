#!/usr/bin/env python3
"""
Database initialization script for LMS
Creates sample users for testing
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import connect_to_mongo, close_mongo_connection, get_database
from app.utils.auth import get_password_hash
from datetime import datetime

async def init_database():
    """Initialize database with sample data"""
    
    # Connect to MongoDB
    await connect_to_mongo()
    db = get_database()
    
    print("🚀 Initializing LMS Database...")
    
    # Sample users data
    sample_users = [
        {
            "name": "Admin User",
            "email": "admin@lms.com",
            "password_hash": get_password_hash("admin123"),
            "role": "admin",
            "created_at": datetime.utcnow()
        },
        {
            "name": "John Employee",
            "email": "john@lms.com",
            "password_hash": get_password_hash("employee123"),
            "role": "employee",
            "created_at": datetime.utcnow()
        },
        {
            "name": "Sarah Manager",
            "email": "sarah@lms.com",
            "password_hash": get_password_hash("employee123"),
            "role": "employee",
            "created_at": datetime.utcnow()
        },
        {
            "name": "Mike Developer",
            "email": "mike@lms.com",
            "password_hash": get_password_hash("employee123"),
            "role": "employee",
            "created_at": datetime.utcnow()
        }
    ]
    
    try:
        # Clear existing users (optional - comment out to keep existing data)
        # await db.users.delete_many({})
        
        # Insert sample users
        for user_data in sample_users:
            # Check if user already exists
            existing_user = await db.users.find_one({"email": user_data["email"]})
            if not existing_user:
                result = await db.users.insert_one(user_data)
                print(f"✅ Created user: {user_data['name']} ({user_data['email']})")
            else:
                print(f"⏭️  User already exists: {user_data['name']} ({user_data['email']})")
        
        print("\n🎉 Database initialization completed!")
        print("\n📋 Sample Login Credentials:")
        print("Admin:")
        print("  Email: admin@lms.com")
        print("  Password: admin123")
        print("\nEmployees:")
        print("  Email: john@lms.com, sarah@lms.com, mike@lms.com")
        print("  Password: employee123")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
    
    finally:
        # Close connection
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(init_database()) 