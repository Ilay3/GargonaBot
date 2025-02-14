import sys
import pytz
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import requests

if len(sys.argv) < 2:
    print("Не указан токен Telegram!")
    sys.exit(1)
TELEGRAM_TOKEN = sys.argv[1]

async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("Переключить Anti-AFK", callback_data="toggle_antiafk")],
        [InlineKeyboardButton("Запустить/Остановить Крафты", callback_data="toggle_cook")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "toggle_antiafk":
        r = requests.post("http://127.0.0.1:5000/antiafk")
        if r.status_code == 200:
            await query.edit_message_text(text="Anti-AFK переключён!")
        else:
            await query.edit_message_text(text="Ошибка: " + r.text)
    elif query.data == "toggle_cook":
        r = requests.post("http://127.0.0.1:5000/cook", data={'dish_count': '5'})
        if r.status_code == 200:
            await query.edit_message_text(text="Крафты переключены!")
        else:
            await query.edit_message_text(text="Ошибка: " + r.text)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).job_queue_timezone(pytz.UTC).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == '__main__':
    main()
