import json

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from handlers.build_scene_handler import build_scene_image_prompt
from services.ask_gpt_with_context import generate_text_with_context
from services.create_system_promts import create_system_prompt
from services.generate_image import generate_image


async def handle_action_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    stats = context.user_data["stats"]
    #обновляем системный промпт в истории, чтобы он соответствовал текущему персонажу
    
    context.user_data['history'][0]['content'] = create_system_prompt(
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

    context.user_data['history'].append({"role": "user", "content": action_text})

    message = await query.message.reply_text("⚔️ Сцена развивается...")

    answer_str_json = await generate_text_with_context(context.user_data['history'])

    print(answer_str_json)

    answer_dic = json.loads(answer_str_json)

    keyboard = [
        [InlineKeyboardButton("действие 1", callback_data="action_1")],
        [InlineKeyboardButton("действие 2", callback_data="action_2")],
        [InlineKeyboardButton("действие 3", callback_data="action_3")],
    ]
    scene_text = answer_dic["scene"] + "\n"
    n = 1
    for action in answer_dic["actions"]:
        scene_text += "\n" + str(n) + ". " + action
        n += 1
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

    context.user_data["history"].append({"role": "assistant", "content": scene_text})

    context.user_data["last_scene_dic"] = answer_dic

    scene_image_path = await generate_image(
        image_prompt,
        reference_image_path=context.user_data["portrait"],
    )

    await message.delete()
    await query.message.reply_photo(
        photo=scene_image_path,
        caption=scene_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )