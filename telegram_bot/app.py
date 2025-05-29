from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
import requests
from os import environ
from models import CustomUser
from database import SessionLocal
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

TELEGRAM_BOT_TOKEN = environ.get("TELEGRAM_BOT_TOKEN")
DJANGO_URL = environ.get("DJANGO_URL", "http://service-app:8000") # URL вашего Django приложения

class OrderNotification(BaseModel):
    user_id: int
    order_id: int

# Инициализация бота
bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build() #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    telegram_id = str(update.effective_user.id)
    phone = update.message.text.split()[-1] if len(update.message.text.split()) > 1 else None

    if not phone:
        await update.message.reply_text("Пожалуйста, укажите номер телефона после /start, например: /start +1234567890")
        return

    with SessionLocal() as db:
        user = db.query(CustomUser).filter(CustomUser.phone == phone).first()
        if not user:
            await update.message.reply_text("Пользователь с таким номером телефона не найден.")
            return

        user.telegram_id = telegram_id
        db.commit()
        await update.message.reply_text("Вы успешно зарегистрированы в системе!")

# Регистрация обработчиков
bot_app.add_handler(CommandHandler("start", start))

@app.on_event("startup")
async def startup_event():
    """Запуск бота при старте FastAPI"""
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()

@app.on_event("shutdown")
async def shutdown_event():
    """Остановка бота при завершении FastAPI"""
    await bot_app.updater.stop()
    await bot_app.stop()
    await bot_app.shutdown()

@app.post("/notify-order/")
async def notify_order(notification: OrderNotification):
    """Отправка уведомления о новом заказе"""
    with SessionLocal() as db:
        user = db.query(CustomUser).filter(CustomUser.id == notification.user_id).first()
        if not user or not user.telegram_id:
            logger.error(f"Пользователь {notification.user_id} не найден или без Telegram ID")
            raise HTTPException(status_code=404, detail="Пользователь не найден или без Telegram ID")

        try:
            await send_telegram_message(
                user.telegram_id,
                f"Вам пришёл новый заказ! ID заказа: {notification.order_id}"
            )
            return {"status": "Уведомление отправлено"}
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления: {e}")
            raise HTTPException(status_code=500, detail=str(e))

async def send_telegram_message(chat_id: str, message: str):
    """Отправка сообщения через Telegram API"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()