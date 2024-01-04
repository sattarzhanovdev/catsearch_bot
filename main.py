
import ccxt
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
import time

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
  update.message.reply_text('Привет, на связи Даниел Ажиев! чтобы узнать цены на монеты пишите команду\n/getprices название монеты\nНапример: /getprices btc/usdt')


def get_prices(update: Update, context: CallbackContext) -> None:
  symbol = context.args[0].upper()

  update.message.reply_text("Подождите пока Ажиев выйдет из тюрьмы...")

  time.sleep(5)

  update.message.reply_text("Дал 500 000$ не отпускает...")

  # Получение цен и изменения цены за последние 24 часа с каждой биржи
  binance_ticker = binance_exchange.fetch_ticker(symbol)
  bybit_ticker = bybit_exchange.fetch_ticker(symbol)
  okex_ticker = okex_exchange.fetch_ticker(symbol)

  # Извлечение необходимой информации
  binance_price = binance_ticker['last']
  bybit_price = bybit_ticker['last']
  okex_price = okex_ticker['last']

  # Comparing prices and finding the cheapest and most expensive exchanges
  cheapest_exchange = min(binance_price, bybit_price, okex_price)
  most_expensive_exchange = max(binance_price, bybit_price, okex_price)

  binance_percent_change = binance_ticker['percentage'] if 'percentage' in binance_ticker else 0
  bybit_percent_change = bybit_ticker['percentage'] if 'percentage' in bybit_ticker else 0
  okex_percent_change = okex_ticker['percentage'] if 'percentage' in okex_ticker else 0

  price_difference = most_expensive_exchange - cheapest_exchange

  response = f'💵 Цена и изменение за последние 24 часа для {symbol}:\n'
  response += f'💵 Binance: Цена: {binance_price}, Изменение: {binance_percent_change}%\n'
  response += f'💵 Bybit: Цена: {bybit_price}, Изменение: {bybit_percent_change}%\n'
  response += f'💵 OKX: Цена: {okex_price}, Изменение: {okex_percent_change}%\n'
  response += f'🟢 Дорогая биржа: {most_expensive_exchange}\n'
  response += f'🔴 Дешевая биржа: {cheapest_exchange}\n'
  response += f'👌 Разница: {price_difference}'
  

  update.message.reply_text(response)
  update.message.reply_text("Ажиев вышел!")


def get_usdt_pairs_info(update: Update, context: CallbackContext) -> None:
    exchanges = [binance_exchange, bybit_exchange, okex_exchange]
    usdt_pairs_info_list = context.user_data.get('usdt_pairs_info_list', [])
    start_index = context.user_data.get('start_index', 0)
    items_per_page = 10

    for exchange in exchanges:
        markets = exchange.fetch_markets()

        for market in markets[start_index:start_index + items_per_page]:
            symbol = market['symbol']
            if market['quote'] == 'USDT':
                try:
                    ticker = exchange.fetch_ticker(symbol)

                    # Проверка наличия значения цены (last)
                    if 'last' in ticker and ticker['last'] is not None:
                        price = ticker['last']
                        volume = ticker['quoteVolume']
                        percent_change = ticker['percentage'] if 'percentage' in ticker else 0

                        coin_info = [symbol, price, volume, percent_change]
                        usdt_pairs_info_list.append(coin_info)
                except ccxt.NetworkError as e:
                    print(f"Network error: {e}")
                except ccxt.ExchangeError as e:
                    print(f"Exchange error: {e}")

    if usdt_pairs_info_list:
        # Собираем информацию в одну строку
        response = "\n".join([f"{i} = {coin_info}" for i, coin_info in enumerate(usdt_pairs_info_list, start=start_index + 1)])
        update.message.reply_text(response)

        # Подготавливаем данные для следующей порции
        context.user_data['usdt_pairs_info_list'] = usdt_pairs_info_list
        context.user_data['start_index'] = start_index + items_per_page

        # Запрашиваем пользователя, хочет ли он еще информации
        update.message.reply_text("Хотите еще информации? (Да/Нет)")

    else:
        update.message.reply_text("На данный момент нет доступных монет с базовой валютой USDT.")

def handle_pagination_response(update: Update, context: CallbackContext) -> None:
    user_response = update.message.text.lower()

    if user_response == 'да':
        get_usdt_pairs_info(update, context)
    else:
        update.message.reply_text("Окончание вывода информации.")


def main() -> None:
  updater = Updater(telegram_bot_token)

  dp = updater.dispatcher
  dp.add_handler(CommandHandler("start", start))
  dp.add_handler(CommandHandler("getprices", get_prices, pass_args=True))
  dp.add_handler(CommandHandler("getAllCoins", get_usdt_pairs_info))
  dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_pagination_response))

  updater.start_polling()
  updater.idle()

if __name__ == '__main__':
  main()
