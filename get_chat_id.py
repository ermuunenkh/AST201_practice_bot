"""
Standalone script — prints the chat ID of anyone who messages the bot.
Run: python get_chat_id.py
Stop: Ctrl+C
"""

import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

load_dotenv()
BOT_TOKEN = os.environ["BOT_TOKEN"]


async def print_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    print(f"Name: {user.full_name} | Username: @{user.username} | Chat ID: {chat.id}")


app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", print_id))
app.add_handler(MessageHandler(filters.ALL, print_id))
print("Listening for messages... (Ctrl+C to stop)")
app.run_polling()
