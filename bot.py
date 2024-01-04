import random
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from handlers import show_more_random_coins_info

# Ваш токен телеграм-бота
telegram_bot_token = "6659955061:AAF-BsLyqbImLtb4oK3KSf3vcvcW7V5zatY"

# Ваши токены и ключи API для каждой биржи
from exchange_utils import binance_api_key, binance_api_secret, bybit_api_key, bybit_api_secret, okex_api_key, okex_api_secret
from exchange_utils import binance_exchange, bybit_exchange, okex_exchange
from exchange_utils import get_common_markets, fetch_ticker

def get_random_10_coins_info(update, context):
    exchanges = {'Binance': binance_exchange, 'Bybit': bybit_exchange, 'OKX': okex_exchange}
    coins_info_list = []

    try:
        common_markets = get_common_markets()

        # Выбираем случайные 10 монет из полученного списка
        selected_markets = random.sample(common_markets, min(10, len(common_markets)))

        for symbol in selected_markets:
            coin_info = {'Binance': '', 'Bybit': '', 'OKEx': ''}

            for exchange_name, exchange in exchanges.items():
                ticker = fetch_ticker(exchange, symbol)

                # Проверка наличия значения цены (last) и объема (baseVolume)
                if ticker and 'last' in ticker and ticker['last'] is not None and 'baseVolume' in ticker and ticker['baseVolume'] > 150000:
                    price = ticker['last']
                    volume = ticker['baseVolume']
                    percent_change = ticker['percentage'] if 'percentage' in ticker else 0

                    coin_info[exchange_name] = f'Цена: {price}, Volume: {volume}, Изменение: {percent_change}%'

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
            response = f'{coin_symbol}.\n'
            for exchange_name, info in coin_info.items():
                response += f'{exchange_name}: {info}\n'
            
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

# Функция для старта бота
def main():
    updater = Updater(telegram_bot_token)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("getRandom10Coins", get_random_10_coins_info))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
