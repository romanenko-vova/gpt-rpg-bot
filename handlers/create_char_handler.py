from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import ContextTypes
from config.states import CREATECHAR, CREATENAME, CREATECLASS, CREATEDESC


async def create_char_handler_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    if query:
        await query.answer()

    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_mainmenu")],
        [
            InlineKeyboardButton(
                "🧙 Создать персонажа", callback_data="create_character_fr"
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет,создай своего персонажа!",
        reply_markup=reply_markup,
    )
    return CREATECHAR


async def create_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Дай имя своему персонажу"
    )
    user_name = update.effective_message.text
    context.user_data["name"] = user_name

    keyboard = [
        [KeyboardButton("⚔️ Воин")],
        [KeyboardButton("🏹 Охотник")],
        [KeyboardButton("🔮 Маг")],
        [KeyboardButton("🗡 Вор")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    user_class = update.effective_message.text
    context.user_data["class"] = user_class
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выбери класс персонажа в клавиатуре справа снизу",
        reply_markup=reply_markup,
    )
    return CREATENAME


async def create_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data["class"] in ["⚔️ Воин", "🏹 Охотник", "🔮 Маг", "🗡 Вор"]:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Опиши своего персонажа!"
        )
    return CREATECLASS


async def create_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    opis_user = update.effective_message.text
    context.user_data["description"] = opis_user
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Имя персонажа: "
        + context.user_data["name"]
        + "\nКласс персонажа: "
        + context.user_data["class"]
        + "\nОписание персонажа: "
        + context.user_data["description"],
    )
    return CREATEDESC
