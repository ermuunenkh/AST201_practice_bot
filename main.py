from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import BOT_TOKEN
from bot.handlers import cmd_start, handle_answer
from database.db_handler import init_db

init_db()

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("ask", cmd_start))
app.add_handler(CallbackQueryHandler(handle_answer))
app.run_polling()
