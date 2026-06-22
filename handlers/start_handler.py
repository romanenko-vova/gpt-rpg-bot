from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.generate_image import generate_image
from config.states import MAINMENU


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'personage_image' not in context.user_data:
        path = await generate_image(
            "Привет, создай мне изображение для персонажа Игоря"
        )
        with open(path, "rb") as image_file:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_file)
        context.user_data['personage_image'] = path

    query = update.callback_query
    if query:
        await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                "🧙 Создать персонажа", callback_data="create_character"
            )
        ],
        [InlineKeyboardButton("👤 Мой персонаж", callback_data="check_character")],
        [InlineKeyboardButton("🎲 Начать игру", callback_data="start_game")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Привет, {update.effective_user.first_name}! Добро пожаловать в игру!",
        reply_markup=reply_markup,
    )
    return MAINMENU
