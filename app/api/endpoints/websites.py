# app/api/endpoints/websites.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.website import WebsiteCreate, WebsiteResponse
from app.crud.website import create_user_website, get_user_websites
from app.auth.dependencies import get_current_user # Assuming this is where your auth logic lives

router = APIRouter()

@router.post("/", response_model=WebsiteResponse)
def add_website(
    website: WebsiteCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return create_user_website(db=db, website=website, user_id=current_user.id)

from typing import List

@router.get("/", response_model=List[WebsiteResponse])
def read_websites(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return get_user_websites(db=db, user_id=current_user.id)