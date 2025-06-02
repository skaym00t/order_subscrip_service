import telebot

from telegram_bot.database import SessionLocal

API_TOKEN = environ.get("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
Пожалуйста, укажите номер телефона после /start, 
например: /start +1234567890\
""")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.text.startswith('/start'):
        phone_number = message.text.split(' ')[1] if len(message.text.split(' ')) > 1 else None
        if phone_number:
            with SessionLocal() as db:
                user = db.query(CustomUser).filter(CustomUser.phone == phone_number).first()
                if not user:
                    bot.send_message(chat_id, "Пользователь с таким номером телефона не найден.")
                    return
                chat_id = message.chat.id
                user.chat_id = str(chat_id)
                db.commit()
                bot.send_message(chat_id, "Вы успешно зарегистрированы в системе!")