# from fastapi import FastAPI
# from pydantic import BaseModel
# from sqlalchemy.orm import Session
# from telegram import Update
# from telegram.ext import (
#     Application,
#     CommandHandler,
#     ContextTypes,
# )
# import requests
# from os import environ
# from models import CustomUser
# from database import SessionLocal
# import logging
# import asyncio
# from typing import Optional
#
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# app = FastAPI()
#
# TELEGRAM_BOT_TOKEN = environ.get("TELEGRAM_BOT_TOKEN")
# DJANGO_URL = environ.get("DJANGO_URL", "http://service-site:8000")  # Обновлено на service-site
#
# class OrderNotification(BaseModel):
#     user_id: Optional[int] = None
#     customer_id: Optional[int] = None
#     customer_name: Optional[str] = None
#     customer_phone: Optional[str] = None
#     executor_id: Optional[int] = None
#     executor_name: Optional[str] = None
#     executor_phone: Optional[str] = None
#     order_id: Optional[int] = None
#     order_title: Optional[str] = None
#     order_description: Optional[str] = None
#     order_price: Optional[float] = None
#     order_status: Optional[str] = None
#
# # Инициализация бота
# bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
#
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Обработчик команды /start"""
#     telegram_id = str(update.effective_user.id)
#     phone = update.message.text.split()[-1] if len(update.message.text.split()) > 1 else None
#
#     if not phone:
#         await update.message.reply_text("Пожалуйста, укажите номер телефона после /start, например: /start +1234567890")
#         return
#
#     with SessionLocal() as db:
#         user = db.query(CustomUser).filter(CustomUser.phone == phone).first()
#         if not user:
#             await update.message.reply_text("Пользователь с таким номером телефона не найден.")
#             return
#
#         user.telegram_id = telegram_id
#         db.commit()
#         await update.message.reply_text("Вы успешно зарегистрированы в системе!")
#
# # Регистрация обработчиков
# bot_app.add_handler(CommandHandler("start", start))
#
# @app.on_event("startup")
# async def startup_event():
#     """Запуск бота при старте FastAPI"""
#     await bot_app.initialize()
#     await bot_app.start()
#     await bot_app.updater.start_polling()
#
# @app.on_event("shutdown")
# async def shutdown_event():
#     """Остановка бота при завершении FastAPI"""
#     await bot_app.updater.stop()
#     await bot_app.stop()
#     await bot_app.shutdown()
#
# @app.post("/notify-create/")
# async def notify_order(notification: OrderNotification):
#     """Отправка уведомления о новом заказе"""
#     logger.debug(f"Получен запрос на /notify-create/: {notification.dict()}")
#     with SessionLocal() as db:
#         user = db.query(CustomUser).filter(CustomUser.id == notification.user_id).first()
#         if not user or not user.telegram_id:
#             logger.warning(f"Уведомление не отправлено: пользователь {notification.user_id} не найден или без Telegram ID")
#             return {"status": "Уведомление не отправлено: пользователь не найден или без Telegram ID"}
#
#         try:
#             await send_telegram_message(
#                 user.telegram_id,
#                 f"{notification.customer_name}, вы выставили заявку: {notification.order_title}"
#             )
#             logger.info(f"Уведомление отправлено пользователю {user.id}")
#             return {"status": "Уведомление отправлено"}
#         except Exception as e:
#             logger.error(f"Ошибка отправки уведомления пользователю {notification.user_id}: {e}")
#             return {"status": f"Уведомление не отправлено: {str(e)}"}
#
# @app.post("/notify-new-order/")
# async def notify_new_order(notification: OrderNotification):
#     """Отправка уведомления о новом заказе исполнителям"""
#     logger.debug(f"Получен запрос на /notify-new-order/: {notification.dict()}")
#     with SessionLocal() as db:
#         users = db.query(CustomUser).filter(CustomUser.is_executor == True, CustomUser.telegram_id.isnot(None)).all()
#         if not users:
#             logger.warning("Уведомления не отправлены: нет исполнителей с Telegram ID")
#             return {"status": "Уведомления не отправлены: нет исполнителей с Telegram ID"}
#
#         sent_count = 0
#         for user in users:
#             try:
#                 await send_telegram_message(
#                     user.telegram_id,
#                     f"Новый заказ: {notification.order_title}. Заказчик: {notification.customer_name}, Телефон: {notification.customer_phone}"
#                 )
#                 logger.info(f"Уведомление отправлено исполнителю {user.id}")
#                 sent_count += 1
#             except Exception as e:
#                 logger.error(f"Ошибка отправки уведомления исполнителю {user.id}: {e}")
#                 continue
#
#         return {"status": f"Уведомления отправлены: {sent_count} из {len(users)} исполнителей"}
#
# @app.post("/notify-take-exec/")
# async def notify_order(notification: OrderNotification):
#     """Отправка уведомления исполнителю о взятии заказа"""
#     logger.debug(f"Получен запрос на /notify-take-exec/: {notification.dict()}")
#     with SessionLocal() as db:
#         user = db.query(CustomUser).filter(CustomUser.id == notification.user_id).first()
#         if not user or not user.telegram_id:
#             logger.warning(f"Уведомление не отправлено: пользователь {notification.user_id} не найден или без Telegram ID")
#             return {"status": "Уведомление не отправлено: пользователь не найден или без Telegram ID"}
#
#         try:
#             await send_telegram_message(
#                 user.telegram_id,
#                 f"{notification.executor_name}, вы взяли в работу заказ: {notification.order_title}. Заказчик: {notification.customer_name}, Телефон: {notification.customer_phone}"
#             )
#             logger.info(f"Уведомление отправлено исполнителю {user.id}")
#             return {"status": "Уведомление отправлено"}
#         except Exception as e:
#             logger.error(f"Ошибка отправки уведомления исполнителю {notification.user_id}: {e}")
#             return {"status": f"Уведомление не отправлено: {str(e)}"}
#
# @app.post("/notify-take-cust/")
# async def notify_order(notification: OrderNotification):
#     """Отправка уведомления заказчику о взятии заказа"""
#     logger.debug(f"Получен запрос на /notify-take-cust/: {notification.dict()}")
#     with SessionLocal() as db:
#         user = db.query(CustomUser).filter(CustomUser.id == notification.customer_id).first()
#         if not user or not user.telegram_id:
#             logger.warning(f"Уведомление не отправлено: пользователь {notification.customer_id} не найден или без Telegram ID")
#             return {"status": "Уведомление не отправлено: пользователь не найден или без Telegram ID"}
#
#         try:
#             await send_telegram_message(
#                 user.telegram_id,
#                 f"{notification.customer_name}, исполнитель {notification.executor_name} взял в работу ваш заказ: {notification.order_title}. Телефон исполнителя: {notification.executor_phone}"
#             )
#             logger.info(f"Уведомление отправлено заказчику {user.id}")
#             return {"status": "Уведомление отправлено"}
#         except Exception as e:
#             logger.error(f"Ошибка отправки уведомления заказчику {notification.customer_id}: {e}")
#             return {"status": f"Уведомление не отправлено: {str(e)}"}
#
# @app.post("/notify-cancel-order/")
# async def notify_cancel_order(notification: OrderNotification):
#     """Отправка уведомления о отмене заказа"""
#     logger.debug(f"Получен запрос на /notify-cancel-order/: {notification.dict()}")
#     with SessionLocal() as db:
#         user = db.query(CustomUser).filter(CustomUser.id == notification.customer_id).first()
#         if not user or not user.telegram_id:
#             logger.warning(f"Уведомление не отправлено: пользователь {notification.customer_id} не найден или без Telegram ID")
#             return {"status": "Уведомление не отправлено: пользователь не найден или без Telegram ID"}
#
#         try:
#             await send_telegram_message(
#                 user.telegram_id,
#                 f"{notification.customer_name}, ваш заказ {notification.order_title} был отменен."
#             )
#             logger.info(f"Уведомление отправлено заказчику {user.id}")
#             return {"status": "Уведомление отправлено"}
#         except Exception as e:
#             logger.error(f"Ошибка отправки уведомления заказчику {notification.customer_id}: {e}")
#             return {"status": f"Уведомление не отправлено: {str(e)}"}
#
# @app.post("/notify-complete-order/")
# async def notify_complete_order(notification: OrderNotification):
#     """Отправка уведомления о завершении заказа"""
#     logger.debug(f"Получен запрос на /notify-complete-order/: {notification.dict()}")
#     with SessionLocal() as db:
#         user = db.query(CustomUser).filter(CustomUser.id == notification.customer_id).first()
#         if not user or not user.telegram_id:
#             logger.warning(f"Уведомление не отправлено: пользователь {notification.customer_id} не найден или без Telegram ID")
#             return {"status": "Уведомление не отправлено: пользователь не найден или без Telegram ID"}
#
#         try:
#             await send_telegram_message(
#                 user.telegram_id,
#                 f"{notification.customer_name}, ваш заказ {notification.order_title} был успешно завершен исполнителем {notification.executor_name}."
#             )
#             logger.info(f"Уведомление отправлено заказчику {user.id}")
#             return {"status": "Уведомление отправлено"}
#         except Exception as e:
#             logger.error(f"Ошибка отправки уведомления заказчику {notification.customer_id}: {e}")
#             return {"status": f"Уведомление не отправлено: {str(e)}"}
#
# async def send_telegram_message(chat_id: str, message: str):
#     """Отправка сообщения через Telegram API"""
#     url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
#     payload = {
#         "chat_id": chat_id,
#         "text": message
#     }
#     response = requests.post(url, json=payload)
#     response.raise_for_status()