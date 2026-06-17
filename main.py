from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
)


from config.config import TOKEN
from config.states import MAINMENU, HELP
from handlers.start_handler import start_handler
from handlers.help_handler import help_handler
    
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
            ],
            HELP: [
                CallbackQueryHandler(pattern="back_to_mainmenu", callback=start_handler),
            ]
        },
        fallbacks=[CommandHandler("start", start_handler)],
    )
    #кикишки
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
