import telebot
from os import environ
from database import SessionLocal
from models import CustomUser

bot = telebot.TeleBot(environ.get("TELEGRAM_BOT_TOKEN"))


@bot.message_handler(commands=['help'])
def send_welcome(message):
    """Отправляет приветственное сообщение с инструкциями, на команду help."""
    bot.reply_to(message, """\
Пожалуйста, укажите номер телефона после /start, 
например: /start +1234567890\
""")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """Обрабатывает текстовые сообщения.
    Отвечает на команду /start и сохраняет номер телефона пользователя."""
    if message.text.startswith('/start'):
        parts = message.text.split(' ')
        if len(parts) < 2:
            bot.reply_to(message, "Пожалуйста, укажите номер телефона после /start")
            return

        phone_number = parts[1].strip()
        chat_id = message.chat.id  # Получаем chat_id из сообщения

        with SessionLocal() as db:
            user = db.query(CustomUser).filter(CustomUser.phone == phone_number).first()
            if not user:
                bot.send_message(chat_id, "Пользователь с таким номером телефона не найден.")
                return

            # Обновляем chat_id пользователя
            user.chat_id = str(chat_id)
            db.commit()
            bot.send_message(chat_id, "Вы успешно зарегистрированы в системе!")
    else:
        bot.reply_to(message, """\
        Пожалуйста, укажите номер телефона после /start, 
        например: /start +1234567890\
        """)


if __name__ == '__main__':
    print('Бот запущен!')
    bot.infinity_polling()