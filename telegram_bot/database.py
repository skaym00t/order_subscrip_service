from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os import environ

DATABASE_URL = environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)