import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

TELEGRAM_TOKEN = "7519203557:AAHodua1TcVgCQqTCtW0vOXLaerrs-p-OU4"

import os
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Загружаем базу знаний из файла
def load_knowledge():
    try:
        with open("knowledge.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Нет базы знаний. Пожалуйста, добавьте файл knowledge.txt."

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот поддержки. Задай вопрос по товарам или доставке.")

# Ответ на обычный текст
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    knowledge = load_knowledge()

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://yourdomain.com",
            "X-Title": "TelegramBot",
        },
        json={
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"Ты — профессиональный и вежливый чат-бот поддержки. "
                        f"Отвечай строго на основе следующей базы знаний:\n{knowledge}"
                        "Отвечай только если в базе есть нужная информация. "
                        "Если вопрос не по теме — отвечай, что не можешь помочь. "
                        "Не перечисляй всё подряд — только суть по запросу."
                    )
                },
                {"role": "user", "content": user_input}
            ]
        }
    )

    if response.status_code == 200:
        data = response.json()
        reply = data["choices"][0]["message"]["content"]
    else:
        reply = f"Ошибка: {response.status_code}\n{response.text}"

    await update.message.reply_text(reply)

# Запуск
def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()

