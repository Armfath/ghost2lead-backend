"""Seed ADMIN users. Run: uv run python scripts/seed_admin.py <email>"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.core.database import db_session_maker
from app.models.lead import Lead  # noqa: F401 - for User.lead relationship
from app.models.user import User
from app.util.enums import UserType


async def seed_admin(email: str) -> None:
    async with db_session_maker() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if user:
            user.user_type = UserType.ADMIN
            await session.commit()
            print(f"Updated {email} to ADMIN")
        else:
            user = User(
                email=email,
                user_type=UserType.ADMIN,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            print(f"Created ADMIN user {email}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/seed_admin.py <email>")
        sys.exit(1)
    email = sys.argv[1]
    asyncio.run(seed_admin(email))


if __name__ == "__main__":
    main()
