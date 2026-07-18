from fastapi import FastAPI, Depends
from app.database.connection import engine, Base
from app.models.user import User
from app.auth.routes import router as auth_router
# Import our new security guard
from app.auth.dependencies import get_current_user
from app.api.endpoints import websites
app = FastAPI()
app.include_router(auth_router)
app.include_router(websites.router, prefix="/websites", tags=["websites"])
Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"status": "SitePulse is officially alive!"}

# --- NEW PROTECTED ROUTE ---
# Notice the `Depends(get_current_user)`? That locks the door!
@app.get("/profile")
def get_user_profile(current_user: User = Depends(get_current_user)):
    return {
        "message": "You have accessed private data!", 
        "user_email": current_user.email,
        "account_active": current_user.is_active
    }
