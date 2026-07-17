from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Replace "YOUR_PASSWORD" with your actual MySQL root password.
# We are naming the database "sitepulse_db"
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Me%40448262@localhost:3306/sitepulse_db"

# The engine is the physical connection to your MySQL server
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# The sessionmaker creates temporary conversations with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# The Base is the blueprint for all our future tables (like Users, Websites)
Base = declarative_base()

# This is a helper function we will use later to open and close connections safely
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()