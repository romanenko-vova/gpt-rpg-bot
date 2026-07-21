from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes

from config.states import CREATECHAR, GET_CLASS, CREATEDESC, GET_NAME, MAINMENU, GET_RASSA


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

    query = update.callback_query
    if query:
        await query.answer()

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Дай имя своему персонажу"
    )
    return GET_NAME


async def get_name_and_ask_rassa(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    if query:
        await query.answer()

    user_name = update.effective_message.text
    context.user_data["name"] = user_name

    keyboard = [
        [KeyboardButton("🧑🏼 Человек")],
        [KeyboardButton("🧝‍♂️ Эльф"),
        KeyboardButton("🧙‍♂️ гном")],
        [KeyboardButton("👹 орк"),
        KeyboardButton("🧛‍♂️ вампир")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выбери расу персонажа в клавиатуре справа снизу",
        reply_markup=reply_markup,
    )

    return GET_RASSA


async def get_rassa_and_ask_class(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    if query:
        await query.answer()

    user_rassa = update.effective_message.text
    context.user_data["rassa"] = user_rassa
    if context.user_data["rassa"] in ["🧑🏼 Человек", "🧝‍♂️ Эльф", "🧙‍♂️ гном", "👹 орк", "🧛‍♂️ вампир"]:
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
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"в нашей игре нельзя играть за расу {update.effective_message.text}, выбери другую расу персонажа в клавиатуре снизу",
        )
        return GET_RASSA
    

    return GET_CLASS


async def get_class_and_ask_description(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    if query:
        await query.answer()

    user_class = update.effective_message.text
    context.user_data["class"] = user_class
    if context.user_data["class"] in ["⚔️ Воин", "🏹 Охотник", "🔮 Маг", "🗡 Вор"]:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Опиши своего персонажа!"
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"в нашей игре нельзя играть за класс {update.effective_message.text}, выбери другой класс персонажа в клавиатуре снизу",
        )
        return GET_CLASS
    return CREATEDESC


async def create_description(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    if query:
        await query.answer()

    opis_user = update.effective_message.text
    context.user_data["description"] = opis_user
    keyboard = [
        [
            InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_character"),
            InlineKeyboardButton("❌ Отменить", callback_data="cancel_character"),
        ],
    ]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Имя персонажа: "
        + context.user_data["name"]
        + "\nРаса персонажа: "
        + context.user_data["rassa"]
        + "\nКласс персонажа: "
        + context.user_data["class"]
        + "\nОписание персонажа: "
        + context.user_data["description"],
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return CREATEDESC


async def cancel_character(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    if query:
        await query.answer()

    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_mainmenu")],
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
        chat_id=update.effective_chat.id,
        text="Создание персонажа отменено.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return CREATECHAR
