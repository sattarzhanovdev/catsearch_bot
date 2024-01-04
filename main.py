
import ccxt
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters

from all import get_random_10_coins_info
from getPrices import get_prices

# Ваши токены и ключи API для каждой биржи
binance_api_key = 'AuZSjtXy2Ij7QiBEGZojT6kFu8qLQSQrroiYHUKgOUR96EfuBsxNY3ssJFxLJr14'
binance_api_secret = 'q197N89pRmuZVsUzJOlCDTYolP9p6OMpcOpLI0MizdPzKhJfsBpsYSqmy8wwyELg'

bybit_api_key = 'fDUu6KSrgeP3ARMbL9'
bybit_api_secret = 'I3fL8LJBgn0eo2xdEoQXwQEAygUAcW7QJ85E'

okex_api_key = '807b990b-152a-483a-a0a4-0fd534404517'
okex_api_secret = '3F86EABDD2D920F231B923CEAA89A80C'

# Your Telegram bot token
telegram_bot_token = "6659955061:AAF-BsLyqbImLtb4oK3KSf3vcvcW7V5zatY"

# Initializing exchange clients
binance_exchange = ccxt.binance({'apiKey': binance_api_key, 'secret': binance_api_secret})
bybit_exchange = ccxt.bybit({'apiKey': bybit_api_key, 'secret': bybit_api_secret})
okex_exchange = ccxt.okx({'apiKey': okex_api_key, 'secret': okex_api_secret})


def start(update: Update, context: CallbackContext) -> None:
  update.message.reply_text('Привет, на связи Даниел Ажиев!\nКоманды:\n/price название монеты - чтобы узнать цену монеты,например: /price btc/usdt\n/all - все монеты')


def main() -> None:
  updater = Updater(telegram_bot_token)

  dp = updater.dispatcher
  dp.add_handler(CommandHandler("start", start))
  dp.add_handler(CommandHandler("price", get_prices, pass_args=True))
  dp.add_handler(CommandHandler("all", get_random_10_coins_info))

  updater.start_polling()
  updater.idle()

if __name__ == '__main__':
  main()
