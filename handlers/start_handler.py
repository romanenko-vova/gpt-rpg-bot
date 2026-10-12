from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from config.states import MAINMENU
from db.users_crud import create_user, get_user_by_tg_id
from db.charackter_crud import get_character_by_tg_id, create_character

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user_by_tg_id(update.effective_user.id)
    if not user:
        user = await create_user(update.effective_user.id, update.effective_user.first_name)
        
    query = update.callback_query
    if query:
        await query.answer()
        await query.delete_message()
    keyboard = []
    if not (context.user_data.get('name') and context.user_data.get('race') and context.user_data.get('class') and context.user_data.get('description') and context.user_data.get('stats') and context.user_data.get('portrait')):
        context.user_data["name"] = get_character_by_tg_id(update.effective_user.id).name if get_character_by_tg_id(update.effective_user.id) else None
        context.user_data["race"] = get_character_by_tg_id(update.effective_user.id).race if get_character_by_tg_id(update.effective_user.id) else None
        context.user_data["class"] = get_character_by_tg_id(update.effective_user.id).class_name if get_character_by_tg_id(update.effective_user.id) else None
        context.user_data["description"] = get_character_by_tg_id(update.effective_user.id).description if get_character_by_tg_id(update.effective_user.id) else None
        context.user_data["stats"] = get_character_by_tg_id(update.effective_user.id).stats if get_character_by_tg_id(update.effective_user.id) else None
        context.user_data["portrait"] = get_character_by_tg_id(update.effective_user.id).portrait if get_character_by_tg_id(update.effective_user.id) else None
    if "portrait" not in context.user_data :
        keyboard += [
            [InlineKeyboardButton("🧙 Создать персонажа", callback_data="create_character")],
        ]
    else:
        keyboard += [
            [InlineKeyboardButton("👤 Мой персонаж", callback_data="check_character")],
            ]
    if "user_id" in user and await get_user_by_tg_id(update.effective_user.id):
        keyboard += [
            [InlineKeyboardButton("🎲 Продолжить игру", callback_data="continue_game")],
        ]
    else:
        keyboard += [
            [InlineKeyboardButton("🎲 Начать игру", callback_data="start_game")],
        ]
    keyboard += [
        [InlineKeyboardButton("❓ Помощь", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Привет, {update.effective_user.first_name}! Добро пожаловать в игру!",
        reply_markup=reply_markup,
    )
    return MAINMENU
