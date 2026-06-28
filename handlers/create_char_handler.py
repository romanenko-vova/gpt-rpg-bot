from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes

from config.states import CREATECHAR, GET_CLASS, CREATEDESC, GET_NAME, MAINMENU


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


async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Дай имя своему персонажу"
    )
    return GET_NAME


async def get_name_and_ask_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_message.text
    context.user_data["name"] = user_name

    keyboard = [
        [KeyboardButton("⚔️ Воин")],
        [KeyboardButton("🏹 Охотник")],
        [KeyboardButton("🔮 Маг")],
        [KeyboardButton("🗡 Вор")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выбери класс персонажа в клавиатуре справа снизу",
        reply_markup=reply_markup,
    )
    
    return GET_CLASS

async def get_class_and_ask_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_class = update.effective_message.text
    context.user_data["class"] = user_class
    if context.user_data["class"] in ["⚔️ Воин", "🏹 Охотник", "🔮 Маг", "🗡 Вор"]:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Опиши своего персонажа!"
        )
    return CREATEDESC


async def create_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    opis_user = update.effective_message.text
    context.user_data["description"] = opis_user
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_character"),
         InlineKeyboardButton("❌ Отменить", callback_data="cancel_character")
        ],
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
    return CREATEDESC

async def cancel_character(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_mainmenu")
        ],
        [
            InlineKeyboardButton(
                "🧙 Создать персонажа заново", callback_data="create_character_fr"
            )
        ],
    ]
    query = update.callback_query
    if query:
        await query.answer()
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Создание персонажа отменено.", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CREATECHAR