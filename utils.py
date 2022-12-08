from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime


def choose_date(args=None):
    now = datetime.now()
    month = now.month
    year = now.year
    if not args and month > 10:
        btns = [
            [
                InlineKeyboardButton(year, callback_data=year),
                InlineKeyboardButton(year + 1, callback_data=year + 1),
            ]
        ]
    elif args and len(list(args)) <= 3:
        btns = [[InlineKeyboardButton(arg, callback_data=arg)]for arg in args]
    else:
        btns = []
        row = []
        for day in args:
            if len(row) == 6:
                btns.append(row)
                row = []
            row.append(InlineKeyboardButton(day, callback_data=day))
        if len(row) > 0:
            btns.append(row)
    return InlineKeyboardMarkup(btns)


def conv_menu(phone_requere=False, del_back_btn=False):
    btns = [
        ['⬅ Назад'],
        ['Меню']
    ]
    if phone_requere:
        btns.insert(0, [KeyboardButton('Отправить номер телефона', request_contact=True)])
    if del_back_btn:
        btns.remove(['⬅ Назад'])
    return ReplyKeyboardMarkup(btns, resize_keyboard=True)


def services_kb(is_admin=False):
    btns = [
        ['Наращивание ресниц'],
        ['Массаж и иглоукалывание'],
        ['Консультация врача'],
        ['Связаться с нами'],
    ]
    if is_admin:
        btns.append(['Мои записи'])
    return ReplyKeyboardMarkup(btns, resize_keyboard=True)


def menu(del_btn=None):
    btns = [
        ['Записаться на приём'],
        ['Прайс'],
        ['Примеры работ'],
        ['Меню'],
    ]
    if del_btn:
        for btn in del_btn:
            btns.remove([btn])
    return ReplyKeyboardMarkup(btns, resize_keyboard=True)
