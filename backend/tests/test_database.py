from app.database import SessionLocal
from app.models import User


def test_database_connection():
    db = SessionLocal()

    test_email = "careerpilot_db_test@example.com"

    try:
        # Remove an old test record if one exists.
        existing_user = (
            db.query(User)
            .filter(User.email == test_email)
            .first()
        )

        if existing_user:
            db.delete(existing_user)
            db.commit()

        # Temporary hash-looking value only for DB testing.
        # Real password hashing is implemented in Milestone 4.
        test_user = User(
            email=test_email,
            password_hash="temporary_test_hash",
        )

        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        saved_user = (
            db.query(User)
            .filter(User.email == test_email)
            .first()
        )

        assert saved_user is not None
        assert saved_user.email == test_email

        print("MYSQL WRITE/READ SUCCESS")
        print("Created user ID:", saved_user.id)

        # Clean up test data.
        db.delete(saved_user)
        db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    test_database_connection()