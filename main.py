import logging

from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    PicklePersistence,
    filters,
)

from config.config import TOKEN
from config.states import (
    CREATE_CHARACTER,
    GAME,
    GET_CLASS,
    GET_DESCRIPTION,
    GET_NAME,
    GET_RACE,
    HELP,
    MAIN_MENU,
    SHOW_CHARACTER,
)
from db.database import create_database
from handlers.create_char_handler import (
    ask_name,
    cancel_character,
    save_class_and_ask_description,
    save_description_and_create_character,
    save_name_and_ask_race,
    save_race_and_ask_class,
    show_character_creation,
)
from handlers.create_char_image_handler import create_character_portrait
from handlers.first_play_handler import (
    continue_game,
    load_checkpoint,
    show_checkpoints,
    start_game,
)
from handlers.help_handler import show_help
from handlers.my_character_handler import show_character
from handlers.play_continue_handler import play_turn
from handlers.start_handler import show_main_menu


def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)

    # Запоминаем, на каком шаге был игрок до перезапуска бота.
    persistence = PicklePersistence(filepath="cache")
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .persistence(persistence)
        .post_init(create_database)
        .build()
    )

    # Для каждого шага указываем, на какие кнопки и сообщения отвечает бот.
    conversation = ConversationHandler(
        entry_points=[CommandHandler("start", show_main_menu)],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(pattern="^help$", callback=show_help),
                CallbackQueryHandler(
                    pattern="^create_character$",
                    callback=show_character_creation,
                ),
                CallbackQueryHandler(
                    pattern="^check_character$", callback=show_character
                ),
                CallbackQueryHandler(pattern="^start_game$", callback=start_game),
                CallbackQueryHandler(pattern="^continue_game$", callback=continue_game),
                CallbackQueryHandler(
                    pattern="^show_checkpoints$", callback=show_checkpoints
                ),
                CallbackQueryHandler(
                    pattern=r"^load_save_\d+$", callback=load_checkpoint
                ),
            ],
            HELP: [
                CallbackQueryHandler(
                    pattern="^back_to_mainmenu$", callback=show_main_menu
                ),
            ],
            CREATE_CHARACTER: [
                CallbackQueryHandler(
                    pattern="^back_to_mainmenu$", callback=show_main_menu
                ),
                CallbackQueryHandler(
                    pattern="^create_character_fr$", callback=ask_name
                ),
            ],
            GET_NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    callback=save_name_and_ask_race,
                ),
            ],
            GET_RACE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    callback=save_race_and_ask_class,
                ),
            ],
            GET_CLASS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    callback=save_class_and_ask_description,
                ),
            ],
            GET_DESCRIPTION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    callback=save_description_and_create_character,
                ),
                CallbackQueryHandler(
                    pattern="^cancel_character$", callback=cancel_character
                ),
                CallbackQueryHandler(
                    pattern="^confirm_character$", callback=show_main_menu
                ),
            ],
            SHOW_CHARACTER: [
                CallbackQueryHandler(
                    pattern="^back_to_mainmenu$", callback=show_main_menu
                ),
            ],
            GAME: [
                CallbackQueryHandler(pattern="^action_[1-3]$", callback=play_turn),
            ],
        },
        fallbacks=[CommandHandler("start", show_main_menu)],
        persistent=True,
        name="conversation",
    )
    application.add_handler(conversation)
    application.add_handler(CommandHandler("image", create_character_portrait))
    application.run_polling()


if __name__ == "__main__":
    main()
