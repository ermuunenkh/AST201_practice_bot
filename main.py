from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import BOT_TOKEN
from bot.handlers import cmd_start, cmd_stats, handle_answer
from bot.utils import ignore, on_startup
from database.db_handler import init_db
from database.question_cleaner import build_question_pool
from src.image_handler import compress_images

init_db()
build_question_pool()
compress_images()

app = ApplicationBuilder().token(BOT_TOKEN).post_init(on_startup).build()
app.add_handler(CommandHandler("ask", cmd_start))
app.add_handler(CommandHandler("stats", cmd_stats))
app.add_handler(CallbackQueryHandler(handle_answer))
app.add_handler(MessageHandler(filters.ALL, ignore))
app.run_polling()
