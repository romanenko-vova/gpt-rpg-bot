from telegram import Update
from telegram.ext import ContextTypes

from config.states import MAINMENU


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello World")
    return MAINMENU
