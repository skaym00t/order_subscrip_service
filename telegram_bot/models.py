from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CustomUser(Base):
    """Модель пользователя для сохранения chat_id в базе данных."""
    __tablename__ = 'clients_customuser' # Имя таблицы в базе данных
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    email = Column(String(254), unique=True, nullable=False)
    phone = Column(String(15), unique=True, nullable=True)
    chat_id = Column(String(50), nullable=True)
    is_executor = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True)