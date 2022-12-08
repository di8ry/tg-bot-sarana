from utils import services_kb, menu, conv_menu, choose_date
from telegram.ext import ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from settings import PRICES, ADMINS
from db import add_user, db
from bson.objectid import ObjectId


def add_reserve(update, context):
    context.user_data['username'] = update.message.chat.username
    update.message.reply_text(
        'Введите Ваше имя: ',
        reply_markup=conv_menu(del_back_btn=True),
    )
    return 'name'


def get_phone(update, context):
    context.user_data['name'] = update.message.text
    update.message.reply_text(
        'Введите Ваш телефон: ',
        reply_markup=conv_menu(True)
    )
    return 'phone'


def get_date(update, context):
    try:
        context.user_data['phone'] = update.message.contact.phone_number
        context.user_data['all_slots'] = list(db.free_slots.find({}))
        update.message.reply_text(
            'Укажите дату приёма: ',
            reply_markup=choose_date(),
        )
        return 'date'
    except AttributeError:
        update.message.reply_text(
            'Введите Ваше имя: ',
            reply_markup=conv_menu(del_back_btn=True),
        )
        return 'name'


def save_date(update, context):
    date = update.message.text
    if date == '⬅ Назад':
        update.message.reply_text(
            'Введите Ваш телефон: ',
            reply_markup=conv_menu(True)
        )
        return 'phone'
    # update.message.reply_text(
    #     f'Вы, {name} записаны на {date}. Если что, позвоним на {phone}.',
    #     reply_markup=services_kb()
    # )
    # add_user(user_id, name, phone, date)
    # return ConversationHandler.END


def greet_user(update, context):
    name = update.message.chat.first_name
    context.user_data['id'] = update.message.chat.id
    text = f'Здравствуйте, {name}, выберите услугу.'
    if update.message.text != '/start':
        text = 'Выберите услугу'
    is_admin = update.message.chat.id in ADMINS
    update.message.reply_text(
        text,
        reply_markup=services_kb(is_admin)
    )
    return ConversationHandler.END


def show_menu(update, context):
    context.user_data['service'] = update.message.text
    del_btn = ['Примеры работ']
    if 'ресниц' in context.user_data['service']:
        del_btn = False
    update.message.reply_text(
        'Что Вас интересует?',
        reply_markup=menu(del_btn)
    )


def show_price(update, context):
    prices = PRICES[context.user_data['service']]
    for price in prices:
        update.message.reply_text(
            ''.join(price),
            reply_markup=menu(['Прайс', 'Примеры работ']),
        )


def show_calendar(update, context):
    update.callback_query.answer()
    data = update.callback_query.data
    if len(data) == 4:
        context.user_data['year'] = data
        free_month = []
        for slot in context.user_data['all_slots']:
            month = slot['date'].split('-')[1]
            if month not in free_month:
                free_month.append(month)
        update.callback_query.message.edit_text(
            f'Год: {data}\nВыберите месяц: ',
            reply_markup=choose_date(free_month)
        )
    elif data.isalpha():
        context.user_data['month'] = data
        free_days = set()
        for slot in context.user_data['all_slots']:
            slot = slot['date'].split('-')
            day, month = int(slot[0]), slot[1]
            if month == data:
                free_days.add(day)
        free_days = sorted(free_days)
        old_text = update.callback_query.message.text.split('\n')[0]
        update.callback_query.message.edit_text(
            f'{old_text}\nМесяц: {data}\nВыберите день: ',
            reply_markup=choose_date(free_days)
        )
    elif len(data) in (1, 2):
        context.user_data['day'] = data
        hours = db.free_slots.find({'date': {'$regex': f'{data}-{context.user_data["month"]}-{context.user_data["year"]}'}})
        hours = [hour['date'].split()[1] for hour in hours]
        print(list(hours))
        print(f'{data}-{context.user_data["month"]}-{context.user_data["year"]}')
        old_text = '\n'.join(update.callback_query.message.text.split('\n')[:-1])
        update.callback_query.message.edit_text(
            f'{old_text}\nДень: {data}\nВыберите время: ',
            reply_markup=choose_date(hours)
        )
    else:
        name = context.user_data['name']
        phone = context.user_data['phone']
        user_id = context.user_data['id']
        username = context.user_data['username']
        service = context.user_data['service']
        context.user_data['hours'] = data
        old_text = '\n'.join(update.callback_query.message.text.split('\n')[:-1])
        update.callback_query.message.edit_text(
            f'Вы, {name} записаны на\n{old_text}\nДень: {data}\nЕсли что, позвоним на {phone}.',
        )
        add_user(user_id, name, phone,
                 f"{context.user_data['day']}-{context.user_data['month']}-{context.user_data['year']} {context.user_data['hours']}",
                 username, service)
        return ConversationHandler.END


def show_all_clients(update, context):
    all_rows = db.clients_data.find({})
    for row in all_rows:
        context.bot.send_message(
            chat_id=ADMINS[0],
            text=f'{row["name"]}, {row["phone"]}, {row["date"]}',
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton('Удалить', callback_data='Удалить ' + str(row['_id']))]]
            )
        )


def del_slot(update, context):
    update.callback_query.answer()
    data = ObjectId(update.callback_query.data.split()[1])
    db.clients_data.delete_one({'_id': data})
    update.callback_query.message.edit_text('Запись удалена!')
