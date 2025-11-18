from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserCreate, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check for duplicate auth0_sub
    db_user = db.query(User).filter(User.auth0_sub == user.auth0_sub).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")

    # Check for duplicate email
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        db_user = User(**user.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="User registration failed due to constraint violation"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(auth0_sub: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.auth0_sub == auth0_sub).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
