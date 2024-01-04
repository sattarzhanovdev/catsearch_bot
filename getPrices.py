from main import binance_exchange, bybit_exchange, okex_exchange, Update, CallbackContext, time

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
