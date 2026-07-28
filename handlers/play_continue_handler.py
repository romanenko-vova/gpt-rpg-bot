from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes

from services.ask_gpt_with_context import generate_text_with_context

async def handle_action_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data  # "action_1", "action_2", "action_3"
    action_number = int(action[-1])
    action_text = context.user_data["last_scene_dic"]["actions"][action_number - 1]

    

    # answer_str_json = await generate_text_with_context(
    #     [
    #         {"role": "system", "content": "Ты помощник RPG игры"},
    #         {"role": "assistant", "content": scene_text},
    #         {"role": "user", "content": action_text},
    #         {"role": "assistant", "content": scene_text},
    #         {"role": "user", "content": action_text},
            
    #     ]
    # )
