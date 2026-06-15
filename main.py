from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
)

from config.config import TOKEN
from config.states import MAINMENU
from handlers.start_handler import start_handler


def main():
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_handler)],
        states={
            MAINMENU: [start_handler],
        },
        fallbacks=[CommandHandler("start", start_handler)],
    )
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
