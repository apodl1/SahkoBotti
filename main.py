import price_processing

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import schedule
import asyncio

logging.basicConfig(
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level = logging.INFO
)

with open('messages/start_message.txt', 'r', encoding='utf-8') as file:
    start_message = file.read().rstrip()

with open('messages/help_message.txt', 'r', encoding='utf-8') as file:
    help_message = file.read().rstrip()

with open('telegram_token.txt', 'r') as file:
    telegram_token = file.read().rstrip()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id = update.effective_chat.id, text = start_message)

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id = update.effective_chat.id, text = price_processing.construct_texts())

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id = update.effective_chat.id, text = help_message)


async def schedule_loop():
    while True:
        schedule.run_pending()
        print("waiting")
        await asyncio.sleep(1 * 60)


if __name__ == '__main__':
    application = ApplicationBuilder().token(telegram_token).build()
    
    start_handler = CommandHandler('start', start)
    price_handler = CommandHandler('hinta', price)
    help_handler = CommandHandler('help', help)
    application.add_handler(start_handler)
    application.add_handler(price_handler)
    application.add_handler(help_handler)
    

    price_processing.get_prices()

    schedule.every().day.at("16:00").do(price_processing.get_prices)

    asyncio.ensure_future(schedule_loop())
    asyncio.get_event_loop().run_forever


    application.run_polling()