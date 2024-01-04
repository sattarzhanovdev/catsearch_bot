from main import binance_exchange, bybit_exchange, okex_exchange, Update, CallbackContext, random, ccxt, MessageHandler, Filters

def get_random_10_coins_info(update: Update, context: CallbackContext) -> None:
    exchanges = {'Binance': binance_exchange, 'Bybit': bybit_exchange, 'OKX': okex_exchange}
    coins_info_list = []

    try:
        # Получаем список всех доступных торговых пар с базовой валютой USDT
        binance_markets = [market['symbol'] for market in binance_exchange.fetch_markets()]
        bybit_markets = [market['symbol'] for market in bybit_exchange.fetch_markets()]
        okex_markets = [market['symbol'] for market in okex_exchange.fetch_markets()]

        common_markets = list(set(binance_markets) & set(bybit_markets) & set(okex_markets))

        # Выбираем случайные 10 монет из полученного списка
        selected_markets = random.sample(common_markets, min(10, len(common_markets)))

        # Сохраняем список выбранных монет в контексте для последующего использования
        context.user_data['selected_markets'] = selected_markets

        for symbol in selected_markets:
            coin_info = {'Binance': '', 'Bybit': '', 'OKX': ''}

            for exchange_name, exchange in exchanges.items():
                try:
                    ticker = exchange.fetch_ticker(symbol)

                    # Проверка наличия значения цены (last) и объема (baseVolume)
                    if 'last' in ticker and ticker['last'] is not None and 'baseVolume' in ticker and ticker['baseVolume'] > 150000:
                        price = ticker['last']
                        volume = ticker['baseVolume']
                        percent_change = ticker['percentage'] if 'percentage' in ticker else 0

                        coin_info[exchange_name] = f'\nЦена: {price}\nVolume: {volume}\nИзменение: {percent_change}%\n'

                    else:
                        coin_info[exchange_name] = 'Нет данных'

                except ccxt.NetworkError as e:
                    print(f"Network error: {e}")
                except ccxt.ExchangeError as e:
                    print(f"Exchange error: {e}")

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


# Функция для отображения еще 10 монет по запросу пользователя
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
