from app.database.db import engine
from app.database.models import Review

if __name__ == "__main__":
    Review.__table__.create(bind=engine)
    print("Seed complete")
