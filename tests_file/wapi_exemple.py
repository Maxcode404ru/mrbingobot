from aiogram.types.base import TelegramObject
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from typing import Dict, Any
import sqlite3
import logging

import requests
from aiogram.types import CallbackQuery
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from datetime import datetime

from random import choices
from api_wapi import *
from dBase import slv

import inline_keyboard
from datetime import *

import os
import dotenv
import time

from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

SLEEP = str(choices([["Спокойной ночи"], ["Спокойной ночи "], ["Спокойной ночи, сладких снов "], ["Спокойной ночи, сладких снов"], ["Доброй ночи "], ["Доброй ночи"] , ["Бай"], ["Бай "], ["Баюшки"], ["Баюшки"]]))
EMOGE = str(choices(["(～﹃～)~zZ", "OwO", "(￣o￣) . z Z", "", ""]))

dotenv.load_dotenv()

PROXY_URL = "http://proxy.server:3128 "


BOT_TOKEN = os.getenv('BOT_TOKEN')
API_key = os.getenv('API_KEY')
base_url = os.getenv('BASE_URL')
conn = sqlite3.connect('', check_same_thread=False)
cursor = conn.cursor()

ADMIN = int(os.getenv('ADMIN'))


def db_table_val(user_id: int, user_name: str, user_city: str, user_choise: str, user_notifi_time: int, user_name_id: str):
    cursor.execute('INSERT or REPLACE INTO db_bot (user_id, user_name, user_city, user_choise, user_notifi_time, user_name_id) VALUES (?, ?, ?, ?, ?, ?)',
                   (user_id, user_name, user_city, user_choise, user_notifi_time, user_name_id))
    conn.commit()


bot = Bot(token=BOT_TOKEN,
          parse_mode='HTML', proxy=PROXY_URL)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# создаём форму и указываем поля
class Form(StatesGroup):
    city = State()
    time1 = State()
    time2 = State()


class dialog(StatesGroup):
    spam = State()
    blacklist = State()
    whitelist = State()


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("/login")
    await message.reply("Привет! Я WApiBot!\n\nМоя работа показывать погоду пользователям в удобное для них время.\n\nЧтобы запустить меня нажмите на /login", reply_markup=markup)
    await bot.send_message(chat_id=ADMIN, text="У нас новый пользователь")


# Начинаем наш диалог


@dp.message_handler(commands=['login'])
async def cmd_login(message: types.Message):
    user_ids = message.from_user.id

    await Form.city.set()
    await message.reply("Укажите город в котором хотите узнать погоду: ")


# Добавляем возможность отмены, если пользователь передумал заполнять
@dp.message_handler(state='*', commands=['cancel'])
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):

    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('ОК')

# Проверяем правильно ли введен город


@dp.message_handler(lambda message: message.text in ["/login", "/start", "/help", "/cancel"], state=Form.city)
async def process_age_invalid(message: types.Message):
    return await message.reply("Непонимаю. Укажите городв котором хотите узнать погоду или используйте /cancel чтобы выйти.")

# Сюда приходит ответ с названием города


@dp.message_handler(state=Form.city)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['city'] = message.text
    await Form.next()
    await message.reply("Хотите ли вы получать получать прогноз погоды? Да/Нет")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("✅", "❌")

    await message.answer("Укажите кнопкой", reply_markup=markup)


# Проверяем хочет ли пользователь получать уведомления
@dp.message_handler(lambda message: message.text not in ["✅", "❌"], state=Form.time1)
async def process_age_invalid(message: types.Message):
    return await message.reply("Непонимаю. Укажите клавиатурой или используйте /cancle чтобы выйти.")


# Принимаем уведомления и узнаем время уведов
@dp.message_handler(state=Form.time1)
async def process_age(message: types.Message, state: FSMContext):
    await Form.next()

    if message.text == "✅":
        user_choise = 1
        us_choise = user_choise
        slv["u_choise"] = us_choise
        await message.reply("Восколько вы хотите узнавать погоду?")
        await state.update_data(time1=message.text)
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, selective=True)
        markup.add("Днем", "Вечером")
        markup.add("Другое")
        await message.answer("Укажите кнопкой.", reply_markup=markup)

    else:
        user_choise = 0
        us_choise = user_choise
        slv["u_choise"] = us_choise
        user_ids = message.from_user.id

        """Выбор время сохранения погоды"""
        us_notification_time = message.text
        print(us_notification_time)
        slv["us_noti_time"] = us_notification_time

        async with state.proxy() as data:
            """Coхранения в словарь, временные"""
            data['time2'] = message.text
            city_name = data['city']
            slv["city"] = city_name  # uscity

            """Сохранение я SQL БД"""
            us_id = message.from_user.id                   # импор id в БД
            us_name = message.from_user.first_name         # импорт имени
            us_naid = message.from_user.last_name          # импорт главного имени
            us_city = data["city"]                         # импорт города
            us_choise = slv["u_choise"]                    # импорт да или нет
            us_noti_time = slv["us_noti_time"]             # импорт времени
            db_table_val(user_id=us_id, user_name=us_name, user_name_id=us_naid,  user_city=us_city,
                         user_choise=us_choise, user_notifi_time=us_noti_time)

            parse_mode = ParseMode.MARKDOWN
            await message.answer("ㅤㅤㅤㅤ❇️ Обработано ❇️\nЧтобы узнать о возможностях бота\nиспользуйте /help.")

        Final_url = base_url + "appid=" + API_key + "&q=" + city_name

        weather_data = requests.get(Final_url).json()

        await state.finish()


# Проверяем время уведомлений
@dp.message_handler(lambda message: message.text not in ["Днем", "Вечером", "Другое"], state=Form.time2)
async def process_gender_invalid(message: types.Message):
    return await message.reply("Не знаю такое время. Укажите время кнопкой на клавиатуре\nИли используйте /cancle чтобы выйти")


# Сохраняем время рассылки уведомлений  (пол), выводим анкету
@dp.message_handler(state=Form.time2)
async def process_gender(message: types.Message, state: FSMContext):
    markup = types.ReplyKeyboardRemove()

    user_ids = message.from_user.id
    """Выбор время сохранения погоды"""
    us_notification_time = message.text

    slv["us_noti_time"] = us_notification_time

    async with state.proxy() as data:
        """Coхранения в словарь, временные"""
        data['time2'] = message.text
        city_name = data['city']
        slv["city"] = city_name  # uscity

        """Сохранение я SQL БД"""
        us_id = message.from_user.id                   # импор id в БД
        us_name = message.from_user.first_name         # импорт имени
        us_naid = message.from_user.username        # импорт главного имени
        us_city = data["city"]                         # импорт города
        us_choise = slv["u_choise"]                    # импорт да или нет
        us_noti_time = slv["us_noti_time"]             # импорт времени
        db_table_val(user_id=us_id, user_name=us_name, user_city=us_city,
                     user_choise=us_choise, user_notifi_time=us_noti_time, user_name_id=us_naid)

        cursor.execute(
            f"SELECT rowid, user_city FROM db_bot WHERE user_id = {user_ids} ")
    # В этой переменной город из БД
        uscity = cursor.fetchone()[1]

        if city_name == uscity:
            Final_url = base_url + "appid=" + API_key + \
                "&q=" + uscity + "&units=metric" + "&lang=ru"
            weather_data = requests.get(Final_url).json()
        else:
            Final_url = base_url + "appid=" + API_key + \
                "&q=" + city_name + "&units=metric" + "&lang=ru"
            weather_data = requests.get(Final_url).json()
        print(weather_data)

        slv["weather_data"] = weather_data
        temp = weather_data["main"]["temp"]
        slv["temp"] = temp
        weatherr = weather_data["weather"]
        slv["weatherrr"] = weatherr

        markup = types.ReplyKeyboardRemove()

        await bot.send_message(
            message.chat.id,
            md.text(
                md.text('Город: ', md.bold(data['city'])),
                md.text('1.', md.bold(data['time1'])),
                md.text('2.', data['time2']),
                sep='\n',
            ),
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN,
        )
        await message.answer("ㅤㅤㅤㅤ❇️ Обработано ❇️\nЧтобы узнать о возможностях бота\nиспользуйте /help.")

    Final_url = base_url + "appid=" + API_key + "&q=" + city_name

    weather_data = requests.get(Final_url).json()

    await state.finish()


"""--------------------------message_handler--------------------------"""


@dp.message_handler(commands="help")
async def process_help_hendler(message: types.Message):
    await message.answer("ㅤㅤㅤㅤㅤℹ️<b>INFO</b>ℹ️\nㅤㅤㅤㅤ<b>Список команд:</b>\n/start - для началы работы с ботом\n/login - чтобы сменить город\n/help \
    - информация о боте\n/weather - узнать погоду\n/wind - узнать ветер\n/suntime - узнать время расвета и заката\n/cancel - отмена заполнения анкеты", reply_markup=inline_keyboard.HELP)


@dp.message_handler(commands="weather")
async def process_weather1_hendler(message: types.Message):

    user_ids = message.from_user.id

    cursor.execute(
        f"SELECT rowid, user_city FROM db_bot WHERE user_id = {user_ids}")
    uscity = cursor.fetchone()[1]  # В этой переменной город из БД
    await message.answer(f"Выбранный город: {uscity}")

    if uscity:
        Final_url = base_url + "appid=" + API_key + \
            "&q=" + uscity + "&units=metric" + "&lang=ru"
        weather_data = requests.get(Final_url).json()

    temp = weather_data["main"]["temp"]
    await message.answer(text=f"Сейчас <b>{weather_data['weather'][0]['description']}</b>\nТемпература составляет: {temp}°C\nОщущается как: {weather_data['main']['feels_like']}°C", reply_markup=inline_keyboard.WEATHER)


@dp.message_handler(commands="wind")
async def process_wind_hendler(message: types.Message):
    user_ids = message.from_user.id
    cursor.execute(
        f"SELECT rowid, user_city FROM db_bot WHERE user_id = {user_ids}")
    uscity = cursor.fetchone()[1]  # В этой переменной город из БД

    if uscity:
        Final_url = base_url + "appid=" + API_key + \
            "&q=" + uscity + "&units=metric" + "&lang=ru"
        weather_data = requests.get(Final_url).json()

    degrees = weather_data['wind']['deg']
    degrees = round(degrees / 45) * 45
    if degrees == 360:
        degrees = 0
    degrees = WindDirection(degrees).name
    degrees = windru[degrees]
    await message.answer(text=f"Направление ветра: <b>{degrees}</b>\nСкорость ветра: {weather_data['wind']['speed']}м/с", reply_markup=inline_keyboard.WIND)


@dp.message_handler(commands="suntime")
async def process_wind_hendler(message: types.Message):
    user_ids = message.from_user.id
    cursor.execute(
        f"SELECT rowid, user_city FROM db_bot WHERE user_id = {user_ids}")
    uscity = cursor.fetchone()[1]  # В этой переменной город из БД

    if uscity:
        Final_url = base_url + "appid=" + API_key + \
            "&q=" + uscity + "&units=metric" + "&lang=ru"
        weather_data = requests.get(Final_url).json()

    suntime1 = datetime.utcfromtimestamp(
        weather_data['sys']['sunrise']).strftime('%H:%M:%S')

    suntime2 = datetime.utcfromtimestamp(
        weather_data['sys']['sunset']).strftime('%H:%M:%S')
    await message.answer(text=f"<b>Примерные данные:</b>\nВосход: {suntime1}\nЗакат: {suntime2}", reply_markup=inline_keyboard.SUN_TIME)


"""--------------------------Callback_query--------------------------"""


@dp.callback_query_handler(text="help")
async def process_help_hendler(callback_query: CallbackQuery):
    await callback_query.message.answer("ㅤㅤㅤㅤㅤℹ️<b>INFO</b>ℹ️\nㅤㅤㅤㅤ<b>Список команд:</b>\n/start - для началы работы с ботом\n/login - чтобы сменить город\n/help \
    - информация о боте\n/weather - узнать погоду\n/wind - узнать ветер\n/suntime - узнать время расвета и заката\n/cancel - отмена заполнения анкеты", reply_markup=inline_keyboard.HELP)


@dp.callback_query_handler(text="weather")
async def process_weather2_hendler(callback_query: CallbackQuery):
    user_ids = callback_query.from_user.id
    print(slv["id"])
    cursor.execute(
        f"SELECT rowid, user_city FROM db_bot WHERE user_id = {user_ids}")
    uscity = cursor.fetchone()[1]  # В этой переменной город из БД
    await callback_query.answer(f"Выбранный город: {uscity}")

    if uscity:
        Final_url = base_url + "appid=" + API_key + \
            "&q=" + uscity + "&units=metric" + "&lang=ru"
        weather_data = requests.get(Final_url).json()

    temp = weather_data["main"]["temp"]
    await callback_query.message.answer(text=f"Сейчас <b>{weather_data['weather'][0]['description']}</b>\nТемпература составляет: {temp}°C\nОщущается как: {weather_data['main']['feels_like']}°C", reply_markup=inline_keyboard.WEATHER)
    await callback_query.answer()


@dp.callback_query_handler(text="wind")
async def process_wind_hendler(callback_query: types.CallbackQuery):
    user_ids = callback_query.from_user.id
    cursor.execute(
        f"SELECT rowid, user_city FROM db_bot WHERE user_id = {user_ids}")
    uscity = cursor.fetchone()[1]  # В этой переменной город из БД

    if uscity:
        Final_url = base_url + "appid=" + API_key + \
            "&q=" + uscity + "&units=metric" + "&lang=ru"
        weather_data = requests.get(Final_url).json()

    degrees = weather_data['wind']['deg']
    degrees = round(degrees / 45) * 45
    if degrees == 360:
        degrees = 0
    degrees = WindDirection(degrees).name
    degrees = windru[degrees]
    await callback_query.message.answer(text=f"Направление ветра: <b>{degrees}</b>\nСкорость ветра: {weather_data['wind']['speed']}м/с", reply_markup=inline_keyboard.WIND)


@dp.callback_query_handler(text="suntime")
async def process_wind_hendler(callback_query: types.CallbackQuery):
    user_ids = callback_query.from_user.id
    cursor.execute(
        f"SELECT rowid, user_city FROM db_bot WHERE user_id = {user_ids}")
    uscity = cursor.fetchone()[1]  # В этой переменной город из БД

    if uscity:
        Final_url = base_url + "appid=" + API_key + \
            "&q=" + uscity + "&units=metric" + "&lang=ru"
        weather_data = requests.get(Final_url).json()

    suntime1 = datetime.utcfromtimestamp(
        weather_data['sys']['sunrise']).strftime('%H:%M:%S')

    suntime2 = datetime.utcfromtimestamp(
        weather_data['sys']['sunset']).strftime('%H:%M:%S')
    await callback_query.message.answer(text=f"<b>Примерные данные:</b>\nВосход: {suntime1}\nЗакат: {suntime2}", reply_markup=inline_keyboard.SUN_TIME)

"""--------------------------message_handler_admin--------------------------"""

# settings


@dp.message_handler(commands="settings")
async def spam(message: types.Message):
    user_ids = int(message.from_user.id)

    if user_ids == ADMIN:
        await message.answer('Команды админов:\n/admin_db - показывает базу данных бота\n/settings - настройки, список команд для админов\n/mailing - команда для рассылки сообщений подписчикам бота\n/dell_admin_db - команда очистки базы данных! НЕРЕКОМЕНДУЕТСЯ ИСПОЛЬЗОВАТЬ!')
    else:
        await message.answer('Error, вы не админ')

# Функция рассылки новостей


@dp.message_handler(commands="mailing")
async def spam(message: types.Message):
    await dialog.spam.set()
    await message.answer('Напиши текст рассылки')

# Функция рассылки новостей


@dp.message_handler(state=dialog.spam)
async def start_spam(message: types.Message, state: FSMContext):
    cursor.execute(f"SELECT user_id FROM db_bot")
    spam_base = cursor.fetchall()
    user_ids = int(message.from_user.id)

    if user_ids == ADMIN:
        for z in range(len(spam_base)):

            await bot.send_message(spam_base[z][0], message.text)
        await message.answer('Рассылка завершена')
        await state.finish()
    else:
        await message.answer('Error, вы не админ')


@ dp.message_handler(commands="admin_db")
async def process_help_hendler(message: types.Message):
    cursor.execute(f"SELECT user_name, user_id, user_name_id FROM db_bot WHERE user_id != 0")
    user_ids = int(message.from_user.id)

    if user_ids == ADMIN:
        db_f = cursor.fetchall()
        db_f = db_f[1:-2]
        print(db_f)
        await message.answer(db_f)
    else:
        await message.answer('Error, вы не админ')

@ dp.message_handler(commands="dell_admin_db")
async def process_help_hendler(message: types.Message):

    user_ids = int(message.from_user.id)

    if user_ids == ADMIN and user_ids == 6172866726:
        cursor.execute(f"DELETE FROM db_bot")
        cursor.execute(f"SELECT user_name, user_id, user_name_id FROM db_bot WHERE user_id != 0")
        db_f = cursor.fetchall()
        conn.commit()
        print(db_f)
        await message.answer(db_f)
    else:
        await message.answer('Error, вы не админ')


"""--------------------------message_by_time--------------------------"""

# app = Client("account", config_file="config.ini")


async def job():

    cursor.execute(f"SELECT user_id FROM db_bot")
    spam_base = cursor.fetchall()
    print(spam_base)
    for question in spam_base:
        for i in question:
            print(i, ' ', end="")
            print("Время")
            SLEEP1 = SLEEP[3:-3]
            EMOGE1 = EMOGE[2:-2]
        await bot.send_message(text=f"{SLEEP1}" +" "+ f"{EMOGE1}", chat_id=i)

scheduler = AsyncIOScheduler()
scheduler.add_job(job, 'cron', day_of_week='mon-sun',
                  hour=18, minute=45, end_date='2023-06-30')
scheduler.start()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
