import jwt
from datetime import datetime, timedelta

# In a real production app, this SECRET_KEY is kept in a hidden .env file!
# We will use this hardcoded string just for our local development milestone.
SECRET_KEY = "my_super_secret_production_key_for_sitepulse"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    to_encode = data.copy()
    
    # Set the token to expire in 60 minutes
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Cryptographically sign the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt