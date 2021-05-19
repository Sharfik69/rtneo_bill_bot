import telebot
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telebot import types
import psycopg2
import settings
from base import BaseModel
from user import User

bot = telebot.TeleBot(settings.__TELEGRAM_TOKEN__, parse_mode=None)
#########################################################
engine = create_engine('sqlite:///test.db', echo=True)
BaseModel.create_base(engine)

session = sessionmaker(bind=engine)()
########################################################
conn = psycopg2.connect(dbname='rtneo', user='cuba',
                        password='cuba', host='localhost')

cursor = conn.cursor()
###############################################################

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.from_user.id, 'Для начала введите команду /auth')

@bot.message_handler(commands=['auth'])
def auth_method(message):
    user_id = message.from_user.id

    check = session.query(User).filter(User.tg_id == user_id).scalar()

    if check is None:
        bot.send_message(message.from_user.id, 'Введите ваш инн')
        bot.register_next_step_handler(message, put_inn)
    else:
        bot.send_message(message.from_user.id, 'Вы уже зарегестрированны')


def put_inn(message):
    inn = message.text
    bot.send_message(message.from_user.id, 'Введите телефон контактного лица')
    bot.register_next_step_handler(message, put_phone, inn)


def put_phone(message, inn):
    phone = message.text
    session.add(User(tg_id=message.from_user.id, inn=inn, phone=phone))
    session.commit()
    bot.send_message(message.from_user.id, 'Вы были записаны в базу')


@bot.message_handler(commands=['get_bill'])
def get_bill(message):
    record = session.query(User).filter(User.tg_id == message.from_user.id).scalar()

    if record is None:
        bot.send_message(message.from_user.id, 'Зарегестрируйтесь /auth')
        return

    inn = record.inn
    phone = record.phone
    ph = ''
    if phone is not None:
        for i in phone:
            if i.isdigit():
                ph += i

    query = 'select id from rtneo_contragent where inn = \'{}\''.format(inn)
    cursor.execute(query)
    record = cursor.fetchone()

    if record is None:
        bot.send_message(message.from_user.id, 'Ваш инн паршивый')
        return

    query = 'select period_, sum_ from rtneo_bill where contragent_id = \'{}\' and is_paid = false'.format(record[0])

    cursor.execute(query)

    records = cursor.fetchall()

    response = ''
    all_sum = 0
    for i in records:
        response += str(i[0]) + " " + str(i[1]) + "\n"
        all_sum += i[1]

    response += "Всего задолженность: {} рублей".format(all_sum)
    bot.send_message(message.from_user.id, response)


bot.polling()
