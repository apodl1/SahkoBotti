import tokens

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sähkön hinnan kertova botti. Lähetä komento /hinta saadaksesi vastauksen.")

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="__Hintatiedot tähän__")

if __name__ == '__main__':
    application = ApplicationBuilder().token(tokens.telegram_token).build()
    
    start_handler = CommandHandler('start', start)
    price_handler = CommandHandler('hinta', price)
    application.add_handler(start_handler)
    application.add_handler(price_handler)
    
    application.run_polling()