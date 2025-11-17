from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from models import Users
from database import SessionLocal
from starlette import status
from .auth import get_current_user, crypt_context

router = APIRouter(
    prefix='/user',
    tags=['user']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user:user_dependency, 
                   db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="authentication failed")
    return db.query(Users).filter(Users.id == user.get('id')).first()


@router.put('/password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user:user_dependency,
                          db:db_dependency,
                          user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail="authentication failed")
    user_model = db.query(Users) \
                   .filter(Users.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="user not found")
    
    if not crypt_context.verify(user_verification.password, user_model.hashed_password): # type: ignore
        raise HTTPException(status_code=401, detail="password mismatch")

    user_model.hashed_password = crypt_context.hash(user_verification.new_password) # type: ignore
    
    db.add(user_model)
    db.commit()