# app/schemas/website.py
from pydantic import HttpUrl, BaseModel

class WebsiteCreate(BaseModel):
    url: HttpUrl

class WebsiteResponse(WebsiteCreate):
    id: int
    user_id: int

    class Config:
        from_attributes = True