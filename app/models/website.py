# app/models/website.py
from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.connection import Base

class Website(Base):
    __tablename__ = "websites"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id")) # Linking to user