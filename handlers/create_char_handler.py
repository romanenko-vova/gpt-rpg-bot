import json
from html import escape

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes

from config.states import (
    CREATECHAR,
    CREATEDESC,
    GET_CLASS,
    GET_NAME,
    GET_RASSA,
)
from handlers.create_char_image_handler import create_character_image
from handlers.generate_stats_handler import generate_stats
from db.users_crud import update_user


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
    await update_user(update.effective_user.id, name=user_name)

    keyboard = [
        [KeyboardButton("🧑🏼 Человек")],
        [KeyboardButton("🧝‍♂️ Эльф")],
        [KeyboardButton("🧙‍♂️ гном")],
        [KeyboardButton("👹 орк")],
        [KeyboardButton("🧛‍♂️ вампир")],
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
    context.user_data["race"] = user_rassa
    if context.user_data["race"] in [
        "🧑🏼 Человек",
        "🧝‍♂️ Эльф",
        "🧙‍♂️ гном",
        "👹 орк",
        "🧛‍♂️ вампир",
    ]:
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
        text='⚙️ Система определяет характеристики...'
    )

    stats = await generate_stats(context=context)
    hp = stats['CON'] * 5
    print(stats)

    context.user_data["stats"] = stats
    await update_user(update.effective_user.id, stats=json.dumps(stats))
    context.user_data["max_hp"] = hp
    context.user_data["hp"] = hp

    # имя/раса/класс/предыстория могут содержать спецсимволы — экранируем под HTML
    name = escape(str(context.user_data["name"]))
    race = escape(str(context.user_data["race"]))
    char_class = escape(str(context.user_data["class"]))
    backstory = escape(str(stats["backstory"]))

    # ширины столбцов по самым длинным словам:
    # слева «Интеллект» = 9 (+1 запас), справа «Телосложение» = 12
    # важно: ❤ без FE0F — иначе len=2 и «Телосложение» уезжает
    left_w, right_w = 9, 12
    stats_table = (
        f"💪 {'Сила':<{left_w}} {stats['STR']:>2}  │  "
        f"🏃 {'Ловкость':<{right_w}} {stats['AGI']:>2}\n"
        f"🧠 {'Интеллект':<{left_w}} {stats['INT']:>2}  │  "
        f"❤️ {'Телосложение':<{right_w}} {stats['CON']:>2}\n"
        f"🗣 {'Харизма':<{left_w}} {stats['CHA']:>2}  │  "
        f"🍀 {'Удача':<{right_w}} {stats['LUCK']:>2}"
    )

    text = (
        f"<b>✨ {name}</b>\n"
        f"<i>{race} · {char_class}</i>\n\n"
        f"<b>Характеристики</b>\n\n"
        f"<code>{stats_table}</code>\n\n"
        f"❤️ <b>HP:</b> {hp}\n\n"
        f"📖 <b>Предыстория</b>\n{backstory}"
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode="HTML",
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=await create_character_image(update, context),
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
