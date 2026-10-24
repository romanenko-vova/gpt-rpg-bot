import json

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from config.states import GAME, MAINMENU
from db.charackter_crud import update_character
from db.games_crud import update_game
from handlers.build_scene_handler import build_scene_image_prompt
from handlers.start_handler import remember_character
from services.ask_gpt_with_context import generate_text_with_context
from services.create_system_promts import create_system_prompt
from services.dice_mechanics import resolve_action_roll
from services.generate_image import generate_image
from services.read_model_json import read_model_json, scene_is_ok


def take_number(data, key):
    # если модель не прислала число, берём 0 и не падаем
    value = data.get(key, 0)
    if type(value) is int:
        return value
    return 0


async def save_fight_progress(telegram_id, context):
    # статы и жизни пишем в базу, не только в память бота
    stats = context.user_data.get("stats")
    if not stats:
        return

    hp = context.user_data.get("hp")
    if type(hp) is not int:
        hp = 0
        context.user_data["hp"] = 0

    max_hp = context.user_data.get("max_hp")
    if type(max_hp) is not int:
        max_hp = hp

    await update_character(
        telegram_id,
        stats=json.dumps(stats),
        hp=hp,
        max_hp=max_hp,
    )


async def handle_action_game(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    if not context.user_data.get("stats"):
        await remember_character(update.effective_user.id, context)

    if not context.user_data.get("stats") or not context.user_data.get("history"):
        await query.message.reply_text(
            "Сначала создай персонажа и начни игру из меню."
        )
        return MAINMENU

    stats = context.user_data["stats"]
    # обновляем системный промпт в истории, чтобы он соответствовал текущему персонажу

    context.user_data["history"][0]["content"] = create_system_prompt(
        name=context.user_data["name"],
        race=context.user_data["race"],
        char_class=context.user_data["class"],
        backstory=stats["backstory"],
        stats=context.user_data["stats"],
    )

    action = query.data  # "action_1", "action_2", "action_3"
    action_number = int(action[-1])
    last_scene_dic = context.user_data["last_scene_dic"]
    action_text = last_scene_dic["actions"][action_number - 1]

    dice_result = resolve_action_roll(
        action_text=action_text,
        stats=context.user_data["stats"],
        char_class=context.user_data["class"],
    )

    context.user_data["history"].append(
        {"role": "user", "content": action_text}
    )

    if dice_result["success"]:
        outcome_text = "✅ Успех"
    else:
        outcome_text = "❌ Провал"
        current_hp = context.user_data.get("hp")
        if type(current_hp) is not int:
            current_hp = 0
        damage = max(1, 5 - dice_result["modifier"])
        context.user_data["hp"] = max(0, current_hp - damage)
        outcome_text += f" (-{damage} HP)"
        await save_fight_progress(update.effective_user.id, context)

    dice_text = (
        f"🎲 Проверка {dice_result['ability']}: d20({dice_result['roll']}) "
        f"+ {dice_result['modifier']} = {dice_result['total']} против DC {dice_result['dc']} — {outcome_text}"
    )

    message = await query.message.reply_text(
        f"{dice_text}\n\n⚔️ Сцена развивается..."
    )

    answer_str_json = await generate_text_with_context(
        context.user_data["history"]
    )

    print(answer_str_json)

    answer_dic = read_model_json(answer_str_json)
    if not scene_is_ok(answer_dic):
        context.user_data["history"].pop()
        await message.edit_text("Не получилось разобрать ответ. Нажми действие ещё раз.")
        return GAME

    keyboard = [
        [InlineKeyboardButton("действие 1", callback_data="action_1")],
        [InlineKeyboardButton("действие 2", callback_data="action_2")],
        [InlineKeyboardButton("действие 3", callback_data="action_3")],
    ]
    scene_text = answer_dic["scene"] + "\n"
    for n, action in enumerate(answer_dic["actions"], start=1):
        scene_text += "\n" + str(n) + ". " + action
    context.user_data["stats"]["STR"] += take_number(answer_dic, "str")
    context.user_data["stats"]["AGI"] += take_number(answer_dic, "agi")
    context.user_data["stats"]["INT"] += take_number(answer_dic, "int")
    context.user_data["stats"]["CON"] += take_number(answer_dic, "con")
    context.user_data["stats"]["CHA"] += take_number(answer_dic, "cha")
    context.user_data["stats"]["LUCK"] += take_number(answer_dic, "luck")
    if type(context.user_data.get("hp")) is not int:
        context.user_data["hp"] = 0
    context.user_data["hp"] += take_number(answer_dic, "hp")
    await save_fight_progress(update.effective_user.id, context)
    await message.edit_text("🖼 Рисую сцену...")

    # генерит английский промпт для генерации картики в шаге игры
    image_prompt = await build_scene_image_prompt(
        scene=answer_dic["scene"],
        race=context.user_data["race"],
        char_class=context.user_data["class"],
    )

    context.user_data["history"].append(
        {"role": "assistant", "content": scene_text}
    )

    context.user_data["last_scene_dic"] = answer_dic

    scene_image_path = await generate_image(
        image_prompt,
        reference_image_path=context.user_data["portrait"],
    )
    await update_game(
        telegram_id=update.effective_user.id,
        last_scene=answer_dic,
        scene_image=scene_image_path,
        history=context.user_data["history"],
    )
    await message.delete()
    await query.message.reply_photo(
        photo=scene_image_path,
        caption=f"{scene_text}\n\n{dice_text}",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return GAME
