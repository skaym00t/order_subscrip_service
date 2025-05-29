from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base() # Базовый класс для моделей SQLAlchemy

class CustomUser(Base):
    __tablename__ = 'clients_customuser' # Имя таблицы в базе данных
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    email = Column(String(254), unique=True, nullable=False)
    phone = Column(String(15), unique=True, nullable=True)
    telegram_id = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)