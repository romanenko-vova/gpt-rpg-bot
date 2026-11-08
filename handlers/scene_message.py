from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def format_scene(scene: dict) -> str:
    # Под описанием выводим список действий с номерами кнопок.
    text = scene["scene"] + "\n"
    for number, action in enumerate(scene["actions"], start=1):
        text += f"\n{number}. {action}"
    return text


async def send_scene(message, image_path: str | None, text: str, action_count: int = 3):
    # Одинаковые кнопки для начала, продолжения и следующего хода.
    buttons = []
    for number in range(1, action_count + 1):
        button = InlineKeyboardButton(
            f"действие {number}", callback_data=f"action_{number}"
        )
        buttons.append([button])

    keyboard = InlineKeyboardMarkup(buttons)
    # Старое сохранение можно открыть, даже если файл картинки уже удалён.
    if image_path and Path(image_path).is_file():
        await message.reply_photo(photo=image_path, caption=text, reply_markup=keyboard)
    else:
        await message.reply_text(text, reply_markup=keyboard)
