from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
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
    await query.delete_message()
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=context.user_data["portrait"],
        caption=f"Имя: {context.user_data['name']}\n"
        + f"Раса: {context.user_data['race']}\n"
        + f"Класс: {context.user_data['class']}\n"
        + f"Описание: {context.user_data['description']}",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return SHOWCHAR
