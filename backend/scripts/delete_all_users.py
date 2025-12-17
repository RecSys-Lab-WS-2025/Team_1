"""
Script to delete all users (DemoProfile) from the database.
This will also cascade delete related souvenirs and feedback entries.
"""
import asyncio
import sys
from pathlib import Path

from sqlalchemy import select

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db_session, init_db
from app.models.entities import DemoProfile
from app.settings import get_settings


async def delete_all_users() -> None:
    """Delete all users (DemoProfile) from the database."""
    settings = get_settings()
    init_db(settings)

    async with await get_db_session() as session:
        # Query all users
        result = await session.execute(select(DemoProfile))
        users = result.scalars().all()
        
        user_count = len(users)
        
        if user_count == 0:
            print("✅ No users found in the database.")
            return
        
        print(f"Found {user_count} user(s) to delete:")
        for user in users:
            print(f"  - User ID: {user.id}, Level: {user.level}, XP: {user.total_xp}")
        
        # Delete all users (cascade will handle souvenirs and feedback)
        for user in users:
            await session.delete(user)
        
        await session.commit()
        
        print(f"\n✅ Successfully deleted {user_count} user(s) and all related data (souvenirs, feedback).")


if __name__ == "__main__":
    asyncio.run(delete_all_users())

