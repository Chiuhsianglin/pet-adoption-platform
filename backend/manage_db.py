#!/usr/bin/env python
"""
Database management CLI for Pet Adoption Platform
"""
import asyncio
import argparse
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import init_db, close_db
from seeds.dev_data import seed_database


async def main():
    parser = argparse.ArgumentParser(description="Database management CLI")
    parser.add_argument(
        "command", 
        choices=["seed", "init", "reset"],
        help="Command to execute"
    )
    parser.add_argument(
        "--force", 
        action="store_true",
        help="Force operation without confirmation"
    )
    
    args = parser.parse_args()
    
    if args.command == "init":
        print("🔧 Initializing database connection...")
        await init_db()
        print("✅ Database initialization completed!")
        
    elif args.command == "seed":
        if not args.force:
            response = input("⚠️  This will add development data to the database. Continue? (y/N): ")
            if response.lower() != 'y':
                print("❌ Operation cancelled.")
                return
        
        print("🌱 Seeding database with development data...")
        await seed_database()
        
    elif args.command == "reset":
        if not args.force:
            response = input("⚠️  This will reset the entire database. Continue? (y/N): ")
            if response.lower() != 'y':
                print("❌ Operation cancelled.")
                return
        
        print("🔄 Resetting database...")
        print("ℹ️  Please run 'alembic upgrade head' after this to recreate tables.")
        # Note: Actual reset would involve dropping all tables
        # For now, this is just a placeholder
        
    await close_db()


if __name__ == "__main__":
    asyncio.run(main())