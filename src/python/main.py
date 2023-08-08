import price_processing

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level = logging.INFO
)

with open('start_message.txt', 'r') as file:
    start_message = file.read()

with open('help_message.txt', 'r') as file:
    help_message = file.read()

with open('telegram_token.txt', 'r') as file:
    telegram_token = file.read()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id = update.effective_chat.id, text = start_message)

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id = update.effective_chat.id, text = price_processing.construct_texts())

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id = update.effective_chat.id, text = help_message)


if __name__ == '__main__':
    application = ApplicationBuilder().token(telegram_token).build()
    
    start_handler = CommandHandler('start', start)
    price_handler = CommandHandler('hinta', price)
    help_handler = CommandHandler('help', help)
    application.add_handler(start_handler)
    application.add_handler(price_handler)
    application.add_handler(help_handler)
    
    application.run_polling()