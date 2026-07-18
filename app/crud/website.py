# app/crud/website.py
from sqlalchemy.orm import Session
from app.models.website import Website
from app.schemas.website import WebsiteCreate

def create_user_website(db: Session, website: WebsiteCreate, user_id: int):
    db_website = Website(url=str(website.url), user_id=user_id)
    db.add(db_website)
    db.commit()
    db.refresh(db_website)
    return db_website

def get_user_websites(db: Session, user_id: int):
    return db.query(Website).filter(Website.user_id == user_id).all()