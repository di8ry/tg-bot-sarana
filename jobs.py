from db import db
from datetime import datetime, timedelta


def check_db(context):
    now = datetime.now()
    date = now - timedelta(days=1)
    date_s = date.strftime('%d-%B-%Y')
    db.free_slots.delete_many({'date': {'$regex': date_s}})
