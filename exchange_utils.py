import ccxt
import random

# Ваши токены и ключи API для каждой биржи
binance_api_key = 'AuZSjtXy2Ij7QiBEGZojT6kFu8qLQSQrroiYHUKgOUR96EfuBsxNY3ssJFxLJr14'
binance_api_secret = 'q197N89pRmuZVsUzJOlCDTYolP9p6OMpcOpLI0MizdPzKhJfsBpsYSqmy8wwyELg'

bybit_api_key = 'fDUu6KSrgeP3ARMbL9'
bybit_api_secret = 'I3fL8LJBgn0eo2xdEoQXwQEAygUAcW7QJ85E'

okex_api_key = '807b990b-152a-483a-a0a4-0fd534404517'
okex_api_secret = '3F86EABDD2D920F231B923CEAA89A80C'

# Инициализация клиентов бирж
binance_exchange = ccxt.binance({'apiKey': binance_api_key, 'secret': binance_api_secret})
bybit_exchange = ccxt.bybit({'apiKey': bybit_api_key, 'secret': bybit_api_secret})
okex_exchange = ccxt.okx({'apiKey': okex_api_key, 'secret': okex_api_secret})

def get_binance_markets():
    return [market['symbol'] for market in binance_exchange.fetch_markets()]

def get_bybit_markets():
    return [market['symbol'] for market in bybit_exchange.fetch_markets()]

def get_okex_markets():
    return [market['symbol'] for market in okex_exchange.fetch_markets()]

def get_common_markets():
    binance_markets = set(get_binance_markets())
    bybit_markets = set(get_bybit_markets())
    okex_markets = set(get_okex_markets())
    return list(binance_markets & bybit_markets & okex_markets)

def fetch_ticker(exchange, symbol):
    try:
        return exchange.fetch_ticker(symbol)
    except ccxt.NetworkError as e:
        print(f"Network error: {e}")
    except ccxt.ExchangeError as e:
        print(f"Exchange error: {e}")
    return None
