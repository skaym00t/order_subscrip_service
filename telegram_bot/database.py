from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os import environ

DATABASE_URL = environ.get("DATABASE_URL") # связь с базой данных в контейнере

engine = create_engine(DATABASE_URL) # Создание движка базы данных и подключение к базе данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)