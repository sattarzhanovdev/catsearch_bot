from telegram.ext import MessageHandler, Filters, CallbackContext
from telegram import Update

from exchange_utils import binance_exchange, bybit_exchange, okex_exchange, get_common_markets, fetch_ticker

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
