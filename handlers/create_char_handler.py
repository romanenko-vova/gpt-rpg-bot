from html import escape

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import ContextTypes

from config.states import (
    CREATE_CHARACTER,
    GET_CLASS,
    GET_DESCRIPTION,
    GET_NAME,
    GET_RACE,
)
from db.character_crud import create_character, update_character
from handlers.create_char_image_handler import create_character_portrait
from handlers.generate_stats_handler import generate_character_stats

RACES = ["🧑🏼 Человек", "🧝‍♂️ Эльф", "🧙‍♂️ гном", "👹 орк", "🧛‍♂️ вампир"]
CLASSES = ["⚔️ Воин", "🏹 Охотник", "🔮 Маг", "🗡 Вор"]


async def show_character_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["waiting_confirm"] = False

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
        text="Привет! Создай своего персонажа.",
        reply_markup=reply_markup,
    )
    return CREATE_CHARACTER


async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["waiting_confirm"] = False

    query = update.callback_query
    if query:
        await query.answer()

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Дай имя своему персонажу"
    )
    await create_character(update.effective_user.id)
    return GET_NAME


async def save_name_and_ask_race(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_message.text
    context.user_data["name"] = name
    await update_character(update.effective_user.id, name=name)

    # Из списка рас делаем кнопки, по одной в каждой строке.
    keyboard = [[KeyboardButton(race)] for race in RACES]
    await update.effective_message.reply_text(
        "Выбери расу персонажа на клавиатуре.",
        reply_markup=ReplyKeyboardMarkup(keyboard),
    )
    return GET_RACE


async def save_race_and_ask_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    race = update.effective_message.text
    if race not in RACES:
        await update.effective_message.reply_text(
            f"За расу {race} играть нельзя. Выбери одну из рас на клавиатуре."
        )
        return GET_RACE

    context.user_data["race"] = race
    await update_character(update.effective_user.id, race=race)

    keyboard = [[KeyboardButton(class_name)] for class_name in CLASSES]
    await update.effective_message.reply_text(
        "Выбери класс персонажа на клавиатуре.",
        reply_markup=ReplyKeyboardMarkup(keyboard),
    )
    return GET_CLASS


async def save_class_and_ask_description(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    class_name = update.effective_message.text
    if class_name not in CLASSES:
        await update.effective_message.reply_text(
            f"Класса {class_name} нет в игре. Выбери класс на клавиатуре."
        )
        return GET_CLASS

    context.user_data["class"] = class_name
    await update_character(update.effective_user.id, class_name=class_name)

    await update.effective_message.reply_text(
        "Опиши своего персонажа!", reply_markup=ReplyKeyboardRemove()
    )
    return GET_DESCRIPTION


async def save_description_and_create_character(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):

    # Когда карточка готова, ждём подтверждение или отмену.
    if context.user_data.get("waiting_confirm"):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Нажми «Подтвердить» или «Отменить».",
        )
        return GET_DESCRIPTION

    description = update.effective_message.text
    context.user_data["description"] = description
    await update_character(update.effective_user.id, description=description)
    keyboard = [
        [
            InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_character"),
            InlineKeyboardButton("❌ Отменить", callback_data="cancel_character"),
        ],
    ]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="⚙️ Система определяет характеристики...",
    )

    stats = await generate_character_stats(context.user_data)
    if not stats:
        await update.effective_message.reply_text(
            "Не получилось получить характеристики. Отправь описание ещё раз."
        )
        return GET_DESCRIPTION

    # Начальное здоровье зависит от телосложения.
    hp = stats["CON"] * 5

    context.user_data["stats"] = stats
    context.user_data["hp"] = hp
    context.user_data["max_hp"] = hp

    await update_character(update.effective_user.id, stats=stats, hp=hp, max_hp=hp)

    # Заменяем специальные символы, чтобы Telegram правильно показал карточку.
    name = escape(str(context.user_data["name"]))
    race = escape(str(context.user_data["race"]))
    char_class = escape(str(context.user_data["class"]))
    backstory = escape(str(stats["backstory"]))

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

    card_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode="HTML",
    )
    drawing_status = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🎨 Рисую портрет...",
    )
    portrait = await create_character_portrait(update, context)
    await drawing_status.delete()
    await card_message.reply_photo(
        photo=portrait,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    context.user_data["waiting_confirm"] = True
    return GET_DESCRIPTION


async def cancel_character(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["waiting_confirm"] = False

    query = update.callback_query
    if query:
        await query.answer()

    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_mainmenu")],
        [
            InlineKeyboardButton(
                "🧙 Создать персонажа заново",
                callback_data="create_character_fr",
            )
        ],
    ]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Создание персонажа отменено.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return CREATE_CHARACTER
