from dotenv import load_dotenv
from src.models.models import User
from fastapi import HTTPException
from sqlalchemy.orm import Session

load_dotenv()


async def subtract_credits(clerk_id: str, db: Session):
    try:
        user = db.query(User).filter(User.clerk_id == clerk_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.credits <= 0:
            return False

        print("Credits before subtraction:", user.credits)

        user.credits -= 1
        db.commit()

        print("Credits after subtraction:", user.credits)
        return True
    except Exception as e:
        print(f"Error subtracting credits: {e}")
        raise HTTPException(status_code=500, detail="Error subtracting credits")
