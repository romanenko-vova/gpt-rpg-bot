from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from config.config import TOKEN
from config.states import MAINMENU, HELP, CREATECHAR, CREATENAME, CREATECLASS, CREATEDESC
from handlers.start_handler import start_handler
from handlers.help_handler import help_handler
from handlers.create_char_handler import create_char_handler_start, create_name, create_class, create_description
def main():
    import logging

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)
    
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_handler)],
        states={
            MAINMENU: [
                CallbackQueryHandler(pattern="help", callback=help_handler),
                CallbackQueryHandler(pattern="create_character", callback=create_char_handler_start),
            ],
            HELP: [
                CallbackQueryHandler(pattern="back_to_mainmenu", callback=start_handler),
            ],
            CREATECHAR: [
                CallbackQueryHandler(pattern="back_to_mainmenu", callback=start_handler),
                CallbackQueryHandler(pattern="create_character_fr", callback=create_name),               
            ],
            CREATENAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, callback=create_name),
            ],
            CREATECLASS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, callback=create_class),
            ],
            CREATEDESC: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, callback=create_description),
            ]
        },
        fallbacks=[CommandHandler("start", start_handler)],
    )
    #кикишки кикиишки
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
