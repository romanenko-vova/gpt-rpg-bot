from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    PicklePersistence
)

from config.config import TOKEN
from config.states import (
    CREATECHAR,
    GET_CLASS,
    GET_NAME,
    HELP,
    MAINMENU,
)
from handlers.create_char_handler import (
    ask_name,
    create_char_handler_start,
    get_class_and_ask_description,
    get_name_and_ask_class,
)
from handlers.help_handler import help_handler
from handlers.start_handler import start_handler


def main():
    import logging

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)
    persistence = PicklePersistence(filepath="cache")

    application = ApplicationBuilder().token(TOKEN).persistence(persistence).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_handler)],
        states={
            MAINMENU: [
                CallbackQueryHandler(pattern="^help$", callback=help_handler),
                CallbackQueryHandler(
                    pattern="^create_character$", callback=create_char_handler_start
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
                MessageHandler(filters.TEXT & ~filters.COMMAND, callback=get_name_and_ask_class),
            ],
            GET_CLASS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, callback=get_class_and_ask_description),
            ],
            # CREATEDESC: [
            #     MessageHandler(
            #         filters.TEXT & ~filters.COMMAND, callback=create_description
            #     ),
            # ],
        },
        fallbacks=[CommandHandler("start", start_handler)],
        persistent=True,
        name="conversation",
    )
    # кикишки кикиишки
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
