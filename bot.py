import ccxt
import time
import random
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, MessageHandler, Filters, CallbackContext

# Ваш токен телеграм-бота
telegram_bot_token = "6659955061:AAF-BsLyqbImLtb4oK3KSf3vcvcW7V5zatY"

# Ваши токены и ключи API для каждой биржи
from exchange_utils import binance_api_key, binance_api_secret, bybit_api_key, bybit_api_secret, okex_api_key, okex_api_secret
from exchange_utils import binance_exchange, bybit_exchange, okex_exchange
from exchange_utils import get_common_markets, fetch_ticker

from telegram.ext import MessageHandler, Filters, CallbackContext
from telegram import Update
from exchange_utils import binance_exchange, bybit_exchange, okex_exchange, get_common_markets, fetch_ticker



def start(update: Update, context: CallbackContext) -> None:
  update.message.reply_text('Привет, на связи Даниел Ажиев!\nКоманды:\n/price название монеты - чтобы узнать цену монеты,например: /price btc/usdt\n/all - все монеты')


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
  response += f'🟢 Дорогая цена: {most_expensive_exchange}\n'
  response += f'🔴 Дешевая цена: {cheapest_exchange}\n'
  response += f'👌 Разница: {price_difference}'
  

  update.message.reply_text(response)
  update.message.reply_text("Ажиев вышел!")



def get_random_10_coins_info(update, context):
    exchanges = {'Binance': binance_exchange, 'Bybit': bybit_exchange, 'OKX': okex_exchange}
    coins_info_list = []

    try:
        common_markets = get_common_markets()

        # Выбираем случайные 10 монет из полученного списка
        selected_markets = random.sample(common_markets, min(10, len(common_markets)))

        for symbol in selected_markets:
            coin_info = {'Binance': '', 'Bybit': '', 'OKX': ''}

            for exchange_name, exchange in exchanges.items():
                ticker = fetch_ticker(exchange, symbol)

                # Проверка наличия значения цены (last) и объема (baseVolume)
                if ticker and 'last' in ticker and ticker['last'] is not None and 'baseVolume' in ticker and ticker['baseVolume'] > 150000:
                    price = ticker['last']

                    volume = ticker['baseVolume']
                    percent_change = ticker['percentage'] if 'percentage' in ticker else 0

                    coin_info[exchange_name] = f'\nЦена: {price}\nVolume: {volume}\nИзменение: {percent_change}%\n'


                else:
                    coin_info[exchange_name] = 'Нет данных'

            # Если хотя бы на одной бирже "Нет данных", не добавляем монету в список
            if all(value != 'Нет данных' for value in coin_info.values()):
                coins_info_list.append((symbol, coin_info))

    except ccxt.NetworkError as e:
        update.message.reply_text("Ошибка сети. Попробуйте позже.")
        return
    except ccxt.ExchangeError as e:
        update.message.reply_text("Ошибка при обращении к бирже. Попробуйте позже.")
        return

    if coins_info_list:
        # Выводим информацию о 10 случайных монетах
        for coin_symbol, coin_info in coins_info_list:
            response = f'💵 {coin_symbol}.\n'
            for exchange_name, info in coin_info.items():
              response += f'👉 {exchange_name}: {info}\n'

            update.message.reply_text(response)

        # Запрашиваем у пользователя, хочет ли он увидеть информацию о еще 10 монет
        update.message.reply_text("Хотите увидеть информацию о еще 10 монет? (Да/Нет)")

        # Добавляем обработчик ответа пользователя
        dp = context.dispatcher
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, show_more_random_coins_info))

        # Сохраняем информацию о 10 монетах для последующего использования
        context.user_data['coins_info_list'] = coins_info_list

    else:
        update.message.reply_text("На данный момент нет доступных монет с базовой валютой USDT и объемом выше 150 тыс.")


def show_more_random_coins_info(update: Update, context: CallbackContext) -> None:
    user_response = update.message.text.lower()

    if user_response == 'да':
        get_random_10_coins_info(update, context)
    elif user_response == 'нет':
        update.message.reply_text("Хорошо, остановимся на этом.")
        # Удаляем обработчик ответа пользователя
        dp = context.dispatcher
        dp.remove_handler(MessageHandler(Filters.text & ~Filters.command, show_more_random_coins_info))
    else:
        update.message.reply_text("Неверный запрос. Пожалуйста, ответьте 'Да' или 'Нет'.")


# Функция для старта бота
def main():
    updater = Updater(telegram_bot_token)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("price", get_prices, pass_args=True))
    dp.add_handler(CommandHandler("all", get_random_10_coins_info))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
