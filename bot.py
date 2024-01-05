from exchange_utils import binance_exchange, bybit_exchange, okex_exchange, get_common_markets, fetch_ticker
from telegram import Update
from telegram.ext import MessageHandler, Filters, CallbackContext
from exchange_utils import get_common_markets, fetch_ticker
from exchange_utils import binance_exchange, bybit_exchange, okex_exchange
import ccxt
import threading
import time
import random
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Ваш токен телеграм-бота
telegram_bot_token = "6659955061:AAF-BsLyqbImLtb4oK3KSf3vcvcW7V5zatY"

# Ваши токены и ключи API для каждой биржи


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        'Привет, я кот-бот CatSearch!\nКоманды:\n/price название монеты - чтобы узнать цену монеты,например: /price btc/usdt\n/all - все монеты')


def get_prices(update: Update, context: CallbackContext) -> None:
	symbol = context.args[0].upper()

	update.message.reply_text("Секундочку...")

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

	price_difference = "{:.2f}".format(most_expensive_exchange - cheapest_exchange)

	response = f'💵 Цена и изменение за последние 24 часа для {symbol}:\n'
	response += f'💵 Binance: Цена: {"{:.2f} USDT".format(binance_price)}, Изменение: {"{:.2f}%".format(binance_percent_change)}\n'
	response += f'💵 Bybit: Цена: {"{:.2f} USDT".format(bybit_price)}, Изменение: {"{:.2f}%".format(bybit_percent_change)}\n'
	response += f'💵 OKX: Цена: {"{:.2f} USDT".format(okex_price)}, Изменение: {"{:.2f}%".format(okex_percent_change)}\n'
	response += f'🟢 Дорогая цена: {"{:.2f} USDT".format(most_expensive_exchange)}\n'
	response += f'🔴 Дешевая цена: {"{:.2f} USDT".format(cheapest_exchange)}\n'
	response += f'👌 Разница: {price_difference} USDT, {float(price_difference) * 89.13} KGS'

	update.message.reply_text(response)


def get_random_10_coins_info(update, context):
	exchanges = {'Binance': binance_exchange, 'Bybit': bybit_exchange, 'OKX': okex_exchange}
	coins_info_list = []

	update.message.reply_text("Подождите...")

	try:
			common_markets = get_common_markets()

			# Выбираем случайные 10 монет из полученного списка
			selected_markets = random.sample(common_markets, min(13, len(common_markets)))

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


def get_top_200_coins_info_threaded(update: Update, context: CallbackContext):
    exchanges = {'Binance': binance_exchange, 'Bybit': bybit_exchange, 'OKX': okex_exchange}
    update.message.reply_text('Секундочку...')

    for exchange_name, exchange in exchanges.items():
        try:
            # Fetching markets from each exchange
            markets = exchange.fetch_markets()

            # Selecting the top 200 markets
            selected_markets = markets[:30]

            # Collecting data for each market
            exchange_data = []
            threads = []

            for market in selected_markets:
                symbol = market['symbol']
                thread = threading.Thread(target=lambda: exchange_data.append((symbol, fetch_ticker(exchange, symbol))))
                thread.start()
                threads.append(thread)

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Send information to Telegram bot
            message = f"{exchange_name}\n"
            for symbol, ticker in exchange_data:
                if ticker and 'last' in ticker:
                    price = ticker['last']
                    volume = ticker['baseVolume']
                    percent_change = ticker.get('percentage', 0)

                    # Check if any value is None or missing
                    if None in (price, volume, percent_change):
                        continue  # Skip this coin if any value is missing

                    message += f"{symbol} - Price: {price} USDT, Volume: {volume}, Change: {percent_change}%\n"

            update.message.reply_text(message)

        except ccxt.NetworkError as e:
            print(f"Network error on {exchange_name}: {e}")
        except ccxt.ExchangeError as e:
            print(f"Exchange error on {exchange_name}: {e}")


# Функция для старта бота


def main():
	updater = Updater(telegram_bot_token)

	dp = updater.dispatcher
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("price", get_prices, pass_args=True))
	dp.add_handler(CommandHandler("all", get_random_10_coins_info))
	dp.add_handler(CommandHandler("blocks", get_top_200_coins_info_threaded))

	updater.start_polling()
	updater.idle()


if __name__ == '__main__':
    main()
