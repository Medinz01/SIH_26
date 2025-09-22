from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base # Updated import
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ayush:hackathon_secret@db/ayur_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This is the modern way to create the Base
Base = declarative_base()