from datetime import datetime

from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.models import Base, Plan, User


settings = get_settings()

connect_args = {}

if settings.database_url.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def init_db():
    Base.metadata.create_all(bind=engine)


def save_user(data: dict):
    with SessionLocal() as db:

        user = db.scalar(
            select(User).where(
                User.user_id == data["user_id"]
            )
        )

        if user:

            for key, value in data.items():
                setattr(user, key, value)

        else:

            user = User(**data)

            db.add(user)

        db.commit()

        db.refresh(user)

        return user


def save_plan(
    user_id: str,
    original_plan: str,
    nutrition_tip: str,
):

    with SessionLocal() as db:

        plan = Plan(
            user_id=user_id,
            original_plan=original_plan,
            nutrition_tip=nutrition_tip,
        )

        db.add(plan)

        db.commit()

        db.refresh(plan)

        return plan


def get_user(user_id: str):

    with SessionLocal() as db:

        return db.scalar(
            select(User).where(
                User.user_id == user_id
            )
        )


def get_original_plan(user_id: str):

    with SessionLocal() as db:

        return db.scalar(
            select(Plan)
            .where(Plan.user_id == user_id)
            .order_by(Plan.id.desc())
        )


def update_plan(
    user_id: str,
    updated_plan: str,
    feedback: str,
):

    with SessionLocal() as db:

        plan = db.scalar(
            select(Plan)
            .where(Plan.user_id == user_id)
            .order_by(Plan.id.desc())
        )

        if not plan:
            return None

        plan.updated_plan = updated_plan
        plan.feedback = feedback
        plan.updated_at = datetime.utcnow()

        db.commit()

        db.refresh(plan)

        return plan


def get_all_users():

    with SessionLocal() as db:

        return db.scalars(
            select(User)
            .order_by(User.created_at.desc())
        ).all()


def get_all_plans():

    with SessionLocal() as db:

        return db.scalars(
            select(Plan)
            .order_by(Plan.created_at.desc())
        ).all()


# =========================================================
# DELETE USER
# =========================================================

def delete_user(user_id: str):

    with SessionLocal() as db:

        user = db.scalar(
            select(User).where(
                User.user_id == user_id
            )
        )

        if not user:
            return False

        # Delete all workout plans belonging to this user
        db.execute(
            delete(Plan).where(
                Plan.user_id == user_id
            )
        )

        # Delete the user
        db.delete(user)

        db.commit()

        return True