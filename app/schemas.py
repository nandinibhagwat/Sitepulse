from pydantic import BaseModel, EmailStr

# This defines the exact format we expect from the frontend when someone signs up
class UserCreate(BaseModel):
    email: EmailStr
    password: str