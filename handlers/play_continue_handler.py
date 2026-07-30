import json

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from handlers.build_scene_handler import build_scene_image_prompt
from handlers.first_play_handler import create_system_prompt
from services.ask_gpt_with_context import generate_text_with_context
from services.generate_image import generate_image


def build_action_prompt_messages(user_data: dict, action_text: str, system_prompt: str):
    messages = [{"role": "system", "content": system_prompt}]
    history = user_data.get("history", [])
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": f"Игрок выбирает действие: {action_text}"})
    return messages


async def handle_action_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action = query.data  # "action_1", "action_2", "action_3"
    action_number = int(action[-1])
    last_scene_dic = context.user_data["last_scene_dic"]
    action_text = last_scene_dic["actions"][action_number - 1]

    if "stats" not in context.user_data:
        await query.message.reply_text(
            "Сначала нужно создать персонажа — нажми «🧙 Создать персонажа»"
        )
        return

    message = await query.message.reply_text("⚔️ Сцена развивается...")
    system_prompt = create_system_prompt(
        name=context.user_data["name"],
        race=context.user_data["race"],
        char_class=context.user_data["class"],
        backstory=context.user_data["backstory"],
        stats=context.user_data["stats"],
    )
    prompt_messages = build_action_prompt_messages(
        user_data=context.user_data,
        action_text=action_text,
        system_prompt=system_prompt,
    )
    answer_str_json = await generate_text_with_context(prompt_messages)
    answer_dic = json.loads(answer_str_json)

    keyboard = [
        InlineKeyboardButton("действие 1", callback_data="action_1"),
        InlineKeyboardButton("действие 2", callback_data="action_2"),
        InlineKeyboardButton("действие 3", callback_data="action_3"),
    ]
    text = answer_dic["scene"] + "\n"
    n = 1
    for action in answer_dic["actions"]:
        text += "\n" + str(n) + ". " + action
        n += 1

    await message.edit_text("🖼 Рисую сцену...")

    image_prompt = await build_scene_image_prompt(
        scene=answer_dic["scene"],
        race=context.user_data["race"],
        char_class=context.user_data["class"],
    )
    context.user_data["history"] = context.user_data.get("history", []) + [
        {"role": "assistant", "content": answer_dic["scene"]}
    ]
    context.user_data["last_scene_dic"] = answer_dic

    scene_image_path = await generate_image(image_prompt)

    await message.delete()
    await query.message.reply_photo(
        photo=scene_image_path,
        caption=text,
        reply_markup=InlineKeyboardMarkup([keyboard]),
    )
