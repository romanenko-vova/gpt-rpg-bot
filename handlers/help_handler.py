from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config.states import HELP

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open(context.user_data['personage_image'], "rb") as image_file:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_file)
    
    
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data='back_to_mainmenu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="это рпг бот, который позволяет создавать персонажей и играть в текстовые приключения. "
        "Вы можете создать персонажа, проверить его характеристики и начать игру. "
        "Если у вас есть вопросы, не стесняйтесь обращаться за помощью к @PELMEN_ZAA! ",
        reply_markup=reply_markup
        )
    
    return HELP