from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes
from config.states import SHOWCHAR

async def show_my_character(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_mainmenu")],
        ]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Имя персонажа: "
        + context.user_data["name"]
        + "\nКласс персонажа: "
        + context.user_data["class"]
        + "\nОписание персонажа: "
        + context.user_data["description"],
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return SHOWCHAR
    