from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
    
)
import json
from telegram.ext import ContextTypes
from services.ask_gpt import generate_text
from services.generate_image import generate_image
from handlers.build_scene_handler import build_scene_image_prompt

def create_system_prompt(name: str, race: str, char_class: str, backstory: str, stats: dict) -> str:
    system_prompt = f"""
    Ты — мастер текстовой RPG. Ты ведёшь игру для одного игрока.

    Персонаж игрока:
    - Имя: {name}
    - Раса: {race}
    - Класс: {char_class}
    - Предыстория: {backstory}
    - Характеристики: STR {stats['STR']}, AGI {stats['AGI']}, INT {stats['INT']}, CON {stats['CON']}, CHA {stats['CHA']}, LUCK {stats['LUCK']}

    Правила:

    - Пиши атмосферно, в стиле тёмного фэнтези
    - Учитывай характеристики персонажа — маг замечает магические детали, воин — тактические
    - Верни ТОЛЬКО JSON без markdown, без ``` и без пояснений.Формат ответа:
    {{   
        "scene": "[описание сцены, в которой находится персонаж]",
        "actions": [
            "[действие 1]",
            "[действие 2]",
            "[действие 3]"
        ]
    }}
    - Не заканчивай игру, сюжет бесконечный
    - Отвечай на русском языке
    """ 
    return system_prompt
    
async def handle_start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if "stats" not in context.user_data:
        await query.message.reply_text(
            "Сначала нужно создать персонажа — нажми «🧙 Создать персонажа»"
        )
        return
    await query.message.reply_text("⚔️ Игра начинается...")
    stats = context.user_data["stats"]

    system_prompt = create_system_prompt(
        name=context.user_data["name"],
        race=context.user_data["race"],
        char_class=context.user_data["class"],
        backstory=context.user_data["backstory"],
        stats=stats
    )
    context.user_data["history"] = [
        {"role": "assistant", "content": system_prompt}
    ]
    context.user_data["answer"] = await generate_text(system_prompt)
    answer = json.loads(context.user_data["answer"])  
    keyboard = [
       InlineKeyboardButton("действие 1", callback_data='action_1'),
       InlineKeyboardButton("действие 2", callback_data='action_2'),
       InlineKeyboardButton("действие 3", callback_data='action_3')
    ]
    text = answer["scene"] + '\n'
    n= 1
    for action in answer["actions"]:
        text += "\n" + str(n) + '. ' +action
        n += 1
    await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup([keyboard])) 
    scene = await create_system_prompt(race=context.user_data["race"], char_class=context.user_data["class"],  backstory=context.user_data["backstory"], stats=context.user_data["stats"], name=context.user_data["name"])
    
    await query.message.reply_text("🖼 Рисую сцену...")
    image_prompt = await build_scene_image_prompt(
        scene=scene,
        race=context.user_data["race"],
        char_class=context.user_data["class"]
    )
    scene_image = await generate_image(image_prompt)

    await query.message.reply_photo(photo=scene_image)
    await query.message.reply_text(scene)
    