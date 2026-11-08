from telegram import Update
from telegram.ext import ContextTypes

from config.states import GAME, MAIN_MENU
from config.stats import STAT_NAMES
from db.character_crud import update_character
from db.games_crud import SCENES_PER_CHECKPOINT, save_checkpoint, save_current_game
from handlers.build_scene_handler import build_scene_image_prompt
from handlers.scene_message import format_scene, send_scene
from handlers.start_handler import load_character
from services.ask_gpt import generate_text_with_history
from services.dice_mechanics import roll_d20
from services.generate_image import generate_image
from services.read_model_json import is_valid_scene, read_model_json
from services.scene_prompts import build_next_scene_prompt

SUMMARY_EVERY_SCENES = 5


def read_stat_change(scene, name):
    # Если модель пропустила число или вернула текст, характеристика не меняется.
    change = scene.get(name)
    if type(change) is int:
        return change
    return 0


async def play_turn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    player = context.user_data
    if not player.get("stats"):
        await load_character(user_id, context)

    stats = player.get("stats")
    history = player.get("history")
    last_scene = player.get("last_scene_dic")
    if (
        not stats
        or not history
        or not is_valid_scene(last_scene, require_three_actions=False)
    ):
        await query.message.reply_text(
            "Открой меню командой /start и начни или продолжи игру."
        )
        return MAIN_MENU

    # Номер кнопки показывает, какую строку выбрать из списка действий.
    action_number = int(query.data[-1])
    if action_number > len(last_scene["actions"]):
        await query.message.reply_text("Такого действия в этой сцене нет.")
        return GAME
    action = last_scene["actions"][action_number - 1]
    story_input = f"Игрок выбрал действие: {action}. "
    dice_text = "🎲 Проверка не нужна"

    # Коммиты Егора (0685126, e7e952a): бросок d20 сравниваем со сложностью сцены.
    difficulty = last_scene.get("dc")
    if last_scene.get("needs_roll") is True and type(difficulty) is int:
        roll = roll_d20()
        if roll >= difficulty:
            result = "✅ Успех"
        else:
            result = "❌ Провал"
        dice_text = f"🎲 Проверка вашей удачи {roll} против DC {difficulty} — {result}"
        story_input += f"Результат броска: {dice_text}."

    # Коммит Артёма (52a6b6d): номер сцены определяет, когда сокращать историю.
    scene_count = player.get("scene_count", 0) + 1
    needs_summary = scene_count % SUMMARY_EVERY_SCENES == 0

    # Готовим копию истории. Если модель ошибётся, сохранённый ход не изменится.
    prompt = build_next_scene_prompt(
        name=player["name"],
        race=player["race"],
        char_class=player["class"],
        backstory=stats["backstory"],
        stats=stats,
    )
    new_history = history.copy()
    new_history[0] = {"role": "system", "content": prompt}
    # Просим сводку в обычном ответе модели, вместе с новой сценой.
    if needs_summary:
        new_history[0]["content"] += (
            '\nДля этого хода добавь в JSON одно дополнительное поле "summary". '
            "Сократи историю, оставляя все ключевые моменты, "
            "которые пригодятся для продолжения игры. Пиши по-русски. "
            "Сохрани важные факты, персонажей, предметы и незавершённые задачи. "
            "Новую сцену опиши отдельно в поле scene."
        )
    new_history.append({"role": "user", "content": story_input})

    status = await query.message.reply_text(f"{dice_text}\n\n⚔️ Сцена развивается...")
    scene = read_model_json(await generate_text_with_history(new_history))
    if not is_valid_scene(scene):
        await status.edit_text("Не получилось разобрать ответ. Нажми действие ещё раз.")
        return GAME

    # Рисуем сцену, затем записываем результат хода в базу.
    await status.edit_text("🖼 Рисую сцену...")
    image_prompt = await build_scene_image_prompt(
        scene=scene["scene"], race=player["race"], char_class=player["class"]
    )
    image_path = await generate_image(
        image_prompt, reference_image_path=player["portrait"]
    )

    new_stats = stats.copy()
    for name in STAT_NAMES:
        new_stats[name] += read_stat_change(scene, name.lower())
    hp = read_stat_change(player, "hp") + read_stat_change(scene, "hp")
    max_hp = player.get("max_hp")
    if type(max_hp) is not int:
        max_hp = hp

    scene_text = format_scene(scene)
    new_history.append({"role": "assistant", "content": scene_text})
    # Автосохранение и контрольная точка должны получить одну историю.
    if needs_summary:
        new_history[0]["content"] = prompt
        summary = scene.pop("summary", None)
        if isinstance(summary, str) and summary.strip():
            new_history = new_history[:2] + [new_history[-1]]
            new_history[1] = {
                "role": "assistant",
                "content": f"Краткая история приключения:\n{summary.strip()}",
            }

    await update_character(user_id, stats=new_stats, hp=hp, max_hp=max_hp)
    await save_current_game(user_id, new_history, scene, image_path, scene_count)

    # Коммиты Егора (e029782): каждые 10 сцен записываем отдельную точку.
    if scene_count % SCENES_PER_CHECKPOINT == 0:
        await save_checkpoint(user_id, new_history, scene, image_path, scene_count)

    player["stats"] = new_stats
    player["hp"] = hp
    player["history"] = new_history
    player["last_scene_dic"] = scene
    player["scene_count"] = scene_count

    await status.delete()
    await send_scene(query.message, image_path, f"{scene_text}\n\n{dice_text}")
    return GAME
