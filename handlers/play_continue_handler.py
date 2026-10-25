import json

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from handlers.build_scene_handler import build_scene_image_prompt
from services.ask_gpt_with_context import generate_text_with_context
from services.create_system_promts import create_system_prompt
from services.dice_mechanics import decide_if_roll_needed, resolve_action_roll
from services.generate_image import generate_image
from db.games_crud import update_game

async def handle_action_game(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

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

    roll_decision = await decide_if_roll_needed(
        action_text=action_text,
        history=context.user_data.get("history", []),
    )

    if roll_decision.get("needs_roll"):
        dice_result = resolve_action_roll(
            action_text=action_text,
            stats=context.user_data["stats"],
            char_class=context.user_data["class"],
            ability=roll_decision.get("ability"),
            dc=int(roll_decision.get("dc", 12)),
        )
        if dice_result["success"]:
            outcome_text = "✅ Успех"
        else:
            outcome_text = "❌ Провал"
            current_hp = context.user_data.get("hp", 0)
            damage = max(1, 5 - dice_result["modifier"])
            context.user_data["hp"] = max(0, current_hp - damage)
            outcome_text += f" (-{damage} HP)"

        dice_text = (
            f"🎲 Проверка {dice_result['ability']}: d20({dice_result['roll']}) "
            f"+ {dice_result['modifier']} = {dice_result['total']} против DC {dice_result['dc']} — {outcome_text}"
        )
        story_input = (
            f"Игрок выбрал действие: {action_text}. "
            f"Решение ведущего: {roll_decision.get('reason', 'Нужна проверка навыка.')}. "
            f"Результат броска: {dice_text}."
        )
    else:
        dice_text = "🎲 Проверка не нужна: действие проходит без риска и без броска."
        story_input = (
            f"Игрок выбрал действие: {action_text}. "
            f"Решение ведущего: {roll_decision.get('reason', 'Действие обычное.')}"
        )

    context.user_data["history"].append({"role": "user", "content": story_input})

    message = await query.message.reply_text(f"{dice_text}\n\n⚔️ Сцена развивается...")

    answer_str_json = await generate_text_with_context(
        context.user_data["history"]
    )

    print(answer_str_json)

    answer_dic = json.loads(answer_str_json)

    keyboard = [
        [InlineKeyboardButton("действие 1", callback_data="action_1")],
        [InlineKeyboardButton("действие 2", callback_data="action_2")],
        [InlineKeyboardButton("действие 3", callback_data="action_3")],
    ]
    scene_text = answer_dic["scene"] + "\n"
    for n, action in enumerate(answer_dic["actions"], start=1):
        scene_text += "\n" + str(n) + ". " + action
    context.user_data["stats"]["STR"] += answer_dic["str"]
    context.user_data["stats"]["AGI"] += answer_dic["agi"]
    context.user_data["stats"]["INT"] += answer_dic["int"]
    context.user_data["stats"]["CON"] += answer_dic["con"]
    context.user_data["stats"]["CHA"] += answer_dic["cha"]
    context.user_data["stats"]["LUCK"] += answer_dic["luck"]
    context.user_data["hp"] += answer_dic["hp"]
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
    