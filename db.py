from pymongo import MongoClient
from datetime import datetime, timedelta
import settings
import certifi

ca = certifi.where()

client = MongoClient(
    f'mongodb+srv://bot-sarana:{settings.DB_PASS}@cluster0.tuyldod.mongodb.net/?retryWrites=true&w=majority',
    tlsCAFile=ca
)

db = client.sarana_bot


def add_user(user_id, name, phone, date, username, service):
    db.clients_data.insert_one({
        'id': user_id,
        'name': name,
        'phone': phone,
        'date': date,
        'username': username,
        'service': service,
    })
    db.free_slots.delete_one({'date': date})
    hours = settings.HOURS[service]
    print(date)
    date, hour = date.split()
    hour = int(hour.split(':')[0])
    for i in range(hours - 1):
        hour += 1
        date = f'{date} {hour}:00'
        db.free_slots.delete_one({'date': date})
        date, hour = date.split()
        hour = int(hour.split(':')[0])


def free_slots(date):
    if not db.free_slots.find_one({'date': date}):
        db.free_slots.insert_one({
            'date': date
        })


def add_default_slots(context):
    now = datetime.now()
    for day in range(1, 91):
        date = now + timedelta(days=day)
        if date.strftime('%w') not in (1, 3):
            date = date.strftime('%d-%B-%Y')
            for hour in range(10, 19):
                free_slots(date + f' {hour}:00')


if __name__ == '__main__':
    add_default_slots()
