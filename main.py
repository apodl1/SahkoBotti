import logging
from logging.handlers import RotatingFileHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from datetime import time
from functools import partial
from typing import cast

from price_processing import ElecPrices

PRICE_UPDATE_HOUR = 15
POLL_INTERVAL = 2

def setup_logger():
  logger = logging.getLogger("sahkobotti")
  logger.setLevel(logging.DEBUG)

  handler = RotatingFileHandler("sahkobotti.log", maxBytes=1_000_000, backupCount=3)
  formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  )
  handler.setFormatter(formatter)

  if not logger.hasHandlers():
    logger.addHandler(handler)

  return logger

#read bot start and help messages from files
with open('messages/start_message.txt', 'r', encoding='utf-8') as file:
    start_message = file.read().rstrip()

with open('messages/help_message.txt', 'r', encoding='utf-8') as file:
    help_message = file.read().rstrip()

#read api-token for telegram bot
with open('.telegram_token', 'r') as file:
    telegram_token = file.read().rstrip()


#functions for sending messages, called by handlers later
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if update.effective_chat:
    await context.bot.send_message(chat_id = update.effective_chat.id, text = start_message)

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE, prices_object: ElecPrices):
  if update.effective_chat:
    await context.bot.send_message(chat_id = update.effective_chat.id, text = prices_object.compose_price_text())

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if update.effective_chat:
    await context.bot.send_message(chat_id = update.effective_chat.id, text = help_message)


# Calls prices_object to fetch new prices. Recurses and runs again in 1h if new prices not available (or fetch fails)
async def fetch_with_retry_job(context: ContextTypes.DEFAULT_TYPE):
  if context.job:
    data = cast(dict[str, ElecPrices], context.job.data)
    prices_object = data['prices_object']
    success = prices_object.fetch_prices_to_dict()
    if not success and context.job_queue and len(context.job_queue.jobs()) == 0:
      context.job_queue.run_once(
        fetch_with_retry_job,
        when=3600,  # in seconds
        data={'prices_object': prices_object}
    )


#main block
if __name__ == '__main__':
  setup_logger()

  elec_prices = ElecPrices() #prices fetched and stored on construction
  application = ApplicationBuilder().token(telegram_token).build()

  #handlers for messages
  start_handler = CommandHandler('start', start)
  price_handler = CommandHandler('hinta', partial(price, prices_object=elec_prices)) #pass prices-object to callback via a partial
  help_handler = CommandHandler('help', help)
  application.add_handler(start_handler)
  application.add_handler(price_handler)
  application.add_handler(help_handler)

  assert application.job_queue #this exists if requirements.txt installed
  # Schedule fetching new prices, the called function recurses and runs again in 1h if new prices not yet available or the fetch fails
  application.job_queue.run_daily(
      fetch_with_retry_job,
      time=time(hour=PRICE_UPDATE_HOUR, minute=0),
      data={'prices_object': elec_prices}
    )

  application.run_polling(poll_interval=POLL_INTERVAL)
