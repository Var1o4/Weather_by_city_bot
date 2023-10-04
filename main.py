import telebot
from telebot import types
import sqlite3
import requests
import json


bot=telebot.TeleBot("6512031081:AAEy399DyqGCErprXJ0y-xL3uWkAb3YPpoI")
name=None
WEATHER_API="2a2499eec8373adf90177cb7a3fdd1c8"

@bot.message_handler(commands=["start"])
def start(message):
    conn = sqlite3.connect('users.sql')
    cur=conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(50), pass varchar(50))')
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, "Введите фио")
    bot.register_next_step_handler(message, user_name)

def user_name(message):
    global name
    name =message.text.strip()
    bot.send_message(message.chat.id, "Введите пароль")
    bot.register_next_step_handler(message, user_pass)

def user_pass(message):
    password =message.text.strip()

    conn = sqlite3.connect('users.sql')
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users (name, pass) VALUES ('%s', '%s')" % (name, password))
    conn.commit()
    cur.close()
    conn.close()

    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Список пользователей", callback_data="users")
    markup.add(button)
    bot.send_message(message.chat.id, "Вы зарегистрированны", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    conn = sqlite3.connect('users.sql')
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users")
    users = cur.fetchall()
    info=""

    for el in users:
        info+=f" Имя: {el[1]}, пароль: {el[2]}\n"
    cur.close()
    conn.close()
    bot.send_message(call.message.chat.id, info)

@bot.message_handler(commands=['weather'])
def weather(message):
    bot.send_message(message.chat.id, "Введите название города для показа погоды!")


@bot.message_handler(content_types=['text'])
def send_weather(message):
    try:
        city=message.text.strip()
        res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API}&units=metric')

        data = json.loads(res.text)
        link_temp=""
        if data['main']['temp']>=30:
            link_temp+="30m.jpg"
        elif data['main']['temp']<30 and data['main']['temp']>=10:
            link_temp+="20.jpg"
        elif data['main']['temp']<10 and data['main']['temp']> (-10):
            link_temp+="0.jpg"
        elif data['main']['temp']<= -10 and data['main']['temp']>= -20:
            link_temp+="m10.jpg"
        elif data['main']['temp']<= -20:
            link_temp+="20m.jpg"
        file=open(link_temp, 'rb')
        bot.reply_to(message, f' Сейчас погода: {data["main"]["temp"]}С \n Ощущается на: {data["main"]["feels_like"]}C\n')
        bot.send_photo(message.chat.id, file)
    except:
         bot.send_message(message.chat.id, f"Вы неправильно ввели название города!")

bot.infinity_polling()