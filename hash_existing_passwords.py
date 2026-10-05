from session import SessionLocal
from model import User
from security import hash_password


db = SessionLocal()

try:
    users = db.query(User).all()

    for user in users:

        if user.password_hash.startswith("$2"):
            print(f"Already hashed: {user.email}")
            continue

        user.password_hash = hash_password(user.password_hash)

        print(f"Hashed password: {user.email}")

    db.commit()

    print("All passwords processed successfully!")

except Exception as e:
    db.rollback()
    print("Error:", e)

finally:
    db.close()