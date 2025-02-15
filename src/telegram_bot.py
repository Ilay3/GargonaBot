import sys
import requests
from telegram.ext import Updater, CommandHandler

# Адрес, где запущен ваш Flask (в main.py)
LOCAL_SERVER_URL = "http://127.0.0.1:5001"

def start(update, context):
    """Команда /start: приветствие."""
    update.message.reply_text(
        "Привет! Я бот для управления бот-приложением.\n"
        "Список команд:\n"
        "/antiafk – Запустить/остановить AntiAFK"
    )

def toggle_antiafk(update, context):
    """Команда /antiafk – обратиться к эндпоинту /toggle_antiafk."""
    try:
        resp = requests.get(f"{LOCAL_SERVER_URL}/toggle_antiafk")
        if resp.status_code == 200:
            update.message.reply_text(f"OK: {resp.text}")
        else:
            update.message.reply_text(f"Ошибка: {resp.status_code} {resp.text}")
    except Exception as e:
        update.message.reply_text(f"Исключение при запросе: {e}")

def main():
    # Проверяем, что пользователь передал токен в аргументах
    if len(sys.argv) < 2:
        print("Использование: python telegram_bot.py <TELEGRAM_BOT_TOKEN>")
        sys.exit(1)

    token = sys.argv[1]
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("antiafk", toggle_antiafk))

    print(">>> Telegram-бот запущен. Ожидаем сообщения...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
