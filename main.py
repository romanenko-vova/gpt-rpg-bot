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
    CREATECHAR,
    CREATEDESC,
    GAME,
    GET_CLASS,
    GET_NAME,
    GET_RASSA,
    HELP,
    MAINMENU,
    SHOWCHAR,
)
from db.database import create_database
from handlers.create_char_handler import (
    ask_name,
    cancel_character,
    create_char_handler_start,
    create_description,
    get_class_and_ask_description,
    get_name_and_ask_rassa,
    get_rassa_and_ask_class,
)
from handlers.create_char_image_handler import create_character_image
from handlers.first_play_handler import handle_start_game
from handlers.help_handler import help_handler
from handlers.my_character_handler import show_my_character
from handlers.play_continue_handler import handle_action_game
from handlers.start_handler import start_handler


def main():
    import logging

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)
    # logger = logging.getLogger(__name__)

    persistence = PicklePersistence(filepath="cache")
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .persistence(persistence)
        .post_init(create_database)
        .build()
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_handler)],
        states={
            MAINMENU: [
                CallbackQueryHandler(pattern="^help$", callback=help_handler),
                CallbackQueryHandler(
                    pattern="^create_character$",
                    callback=create_char_handler_start,
                ),
                CallbackQueryHandler(
                    pattern="^check_character$", callback=show_my_character
                ),
                CallbackQueryHandler(
                    pattern="^start_game$", callback=handle_start_game
                ),
            ],
            HELP: [
                CallbackQueryHandler(
                    pattern="^back_to_mainmenu$", callback=start_handler
                ),
            ],
            CREATECHAR: [
                CallbackQueryHandler(
                    pattern="^back_to_mainmenu$", callback=start_handler
                ),
                CallbackQueryHandler(
                    pattern="^create_character_fr$", callback=ask_name
                ),
            ],
            GET_NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    callback=get_name_and_ask_rassa,
                ),
            ],
            GET_RASSA: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    callback=get_rassa_and_ask_class,
                ),
            ],
            GET_CLASS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    callback=get_class_and_ask_description,
                ),
            ],
            CREATEDESC: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    callback=create_description,
                ),
                CallbackQueryHandler(
                    pattern="^cancel_character$", callback=cancel_character
                ),
                CallbackQueryHandler(
                    pattern="^confirm_character$", callback=start_handler
                ),
            ],
            SHOWCHAR: [
                CallbackQueryHandler(
                    pattern="^back_to_mainmenu$", callback=start_handler
                ),
            ],
            GAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, callback=handle_start_game
                ),
                CallbackQueryHandler(
                    pattern="^action_[1-3]$", callback=handle_action_game
                ),
            ],
        },
        fallbacks=[CommandHandler("start", start_handler)],
        persistent=True,
        name="conversation",
    )
    # кикишки кикиишки
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("image", create_character_image))
    application.run_polling()
    application.add_handler(
        CallbackQueryHandler(handle_start_game, pattern="^start_game$")
    )


if __name__ == "__main__":
    main()
