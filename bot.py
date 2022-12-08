from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from handlers import greet_user, show_price, show_menu, add_reserve, get_phone,\
    get_date, save_date, show_calendar, show_all_clients, del_slot
import settings
from jobs import check_db
from db import add_default_slots
from datetime import time


def main():
    bot = Updater(settings.API_TOKEN)
    dp = bot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(MessageHandler(Filters.regex('^(Наращивание ресниц)$'), show_menu))
    dp.add_handler(MessageHandler(Filters.regex('^(Массаж и иглоукалывание)$'), show_menu))
    dp.add_handler(MessageHandler(Filters.regex('^(Консультация врача)$'), show_menu))

    dp.add_handler(MessageHandler(Filters.regex('^(Меню)$'), greet_user))
    dp.add_handler(MessageHandler(Filters.regex('^(Прайс)$'), show_price))
    dp.add_handler(MessageHandler(Filters.regex('^(Мои записи)$'), show_all_clients))

    conv = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('^(Записаться на приём)$'), add_reserve)
        ],
        states={
            'name': [
                MessageHandler(Filters.text, get_phone)
            ],
            'phone': [
                MessageHandler(Filters.regex('^(⬅ Назад)$'), get_date),
                MessageHandler(Filters.contact, get_date)
            ],
            'date': [
                MessageHandler(Filters.regex('^(⬅ Назад)$'), save_date),
                MessageHandler(Filters.text, save_date)
            ],
        },
        fallbacks=[],
        allow_reentry=True
    )
    dp.add_handler(conv)
    dp.add_handler(CallbackQueryHandler(del_slot, pattern='Удалить'))
    dp.add_handler(CallbackQueryHandler(show_calendar))
    jq = bot.job_queue
    jq.run_repeating(check_db, interval=86400, first=86400)
    jq.run_monthly(add_default_slots, day=10, when=time(1, 0))

    bot.start_polling()
    bot.idle()


if __name__ == '__main__':
    # add_default_slots(None)
    main()
