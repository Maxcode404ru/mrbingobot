
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from keyboards import *
from create_bingo import creature_new_bingo
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from text_fonts_exemple import *
from states import *
import sqlite3
# для преобразования в байтовые обьекты
import pickle
from io import BytesIO
from aiogram.types import InputFile
import re
from aiogram.dispatcher.filters import Text
from aiogram import Dispatcher, types
from aiogram.types import ReplyKeyboardRemove
import random
from functions import *
import os # для удаления фото
from create_bot import bot, dp

def is_hex_color(color):
    # проверка есть ли такой цвет
    pattern = re.compile(r'^#(?:[0-9a-fA-F]{3}){1,2}$')
    return bool(pattern.match(color))
def is_const_color(color):
    # проверка есть ли такой цвет на английском языке
    if color == "brown" or color == "pink" or color ==  "purple"or color == 'black':
        return True
    else:
        return False

# открываем БД
conn = sqlite3.connect('bingo_database.db')
cursor = conn.cursor()


#dp = Dispatcher( bot, storage=storage)


cursor.execute('''CREATE TABLE IF NOT EXISTS bingo_data
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name_user,
                    number_cells INTEGER,
                    background_theme TEXT,
                    background_theme_photo BLOB,
                    color_palette TEXT,
                    two_colors TEXT,
                    color_selection TEXT,
                    name_bingo TEXT,
                    font TEXT,
                    text_cells TEXT,
                    approved_bingo,
                    chat_id)''')
conn.commit()


@dp.message_handler(text=['🆕 Создать бинго','/new_bingo', ])
async def new_bingo(message: types.Message):

    await message.answer("Выбери количество ячеек")
    await Form.number_cells.set()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("3x3", "4x4", "5x5")
    markup.add("Назад")

    await message.answer("Можете указать кнопкой", reply_markup=markup)

@dp.message_handler(state=Form.number_cells)
async def get_number_cells(message: types.Message, state: FSMContext):
    if message.text == '/stop' or message.text == 'Назад': # СДЕЛАТЬ ОБРАБОТЧИК КОТОРЫЙ РЕАГИРУЕТ НА ЧИСЛА КРОМЕ 3 4 5
        await state.finish()
        await message.reply("Создание бинго остановлено", reply_markup=menu_keyboard)
        return
    try:
        if message.text == '3x3' or message.text == '4x4' or message.text == '5x5':
            if message.text == '3x3':
                async with state.proxy() as data:
                    data['number_cells'] = 3
            if message.text == '4x4':
                async with state.proxy() as data:
                    data['number_cells'] = 4
            if message.text == '5x5':
                async with state.proxy() as data:
                    data['number_cells'] = 5
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add("Фото", "Цвет")
            markup.add("Назад")
            await message.answer("🖼️ Какой сделаем фон?\nпришли цвет фона либо же каринку которую хочешь поставить на фон?", reply_markup=markup)
            await Form.background_theme.set()
        else:
           raise ValueError("Выбери число от 3 до 5 ")
    except ValueError:
        await message.reply("Выбери число от 3 до 5 ")
        return

@dp.message_handler(state=Form.background_theme)
async def get_background_theme(message: types.Message, state: FSMContext):
    if message.text == '/stop' or message.text == 'Назад':
        await state.finish()
        await message.reply("Создание бинго остановлено", reply_markup=menu_keyboard)
        return
    try:

        async with state.proxy() as data:
            if message.text == 'Фото':
                data['background_theme'] = message.text
                await message.answer("Пришли фотографию для фона", )
                await Form.background_theme_photo.set()
            elif message.text == 'Цвет':
                data['background_theme'] = message.text
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
                #markup.add("brown", "pink", "purple", 'black')
                await message.answer('🎨 Введи или выбери цвет фона\nМожно вводить цвета в HEX формате\n\nПример: #faf3dd\n\nОзнакомиться с палитрой и получить цвет в формате HEX можно на сайте https://csscolor.ru или через поиск в браузере по запросу "HEX палитра"', reply_markup=types.ReplyKeyboardRemove(), disable_web_page_preview=True)
                await Form.background_theme_color.set()
            else:
                raise ValueError("Извините, я не понимаю, что это за фон. Пожалуйста, выберите фото или цвет.")
    except ValueError:
        await message.reply("Извините, я не понимаю, что это за фон. Пожалуйста, выберите фото или цвет.")
        return

@dp.message_handler(state=Form.background_theme_photo, content_types=['photo', 'text'])
async def get_background_theme_photo(message: types.Message, state: FSMContext):
    if message.text == '/stop' or message.text == 'Назад':
        await state.finish()
        await message.reply("Создание бинго остановлено", reply_markup=menu_keyboard)
        return
    try:
        if message.content_type == 'photo':
            async with state.proxy() as data:
                # Получаем последнее фото из сообщения
                file_id = message.photo[-1].file_id
                # Загружаем файл с сервера Telegram
                file = await bot.get_file(file_id)
                # Создаем уникальное имя файла с использованием id пользователя
                file_name = f'{message.from_user.id}.png'
                # Сохраняем файл на диск
                file_path = await file.download(destination_file=f'photo/{file_name}')
                data['background_photo_name'] = file_name
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add("2 цвета", "1 цвет")
            markup.add("Назад")
            await message.answer("🎨Выбери цветовую палитру", reply_markup=markup)
            await Form.color_palette.set()
        elif message.content_type == 'text':
            await message.reply("Вы отправили текст! Пришлите фото")
    except Exception as e:
        await message.reply(f"Произошла ошибка при загрузке фото: {str(e)}")
        return

@dp.message_handler(state=Form.background_theme_color)
async def get_color_selection(message: types.Message, state: FSMContext):
    if message.text == '/stop' or message.text == 'Назад':
        await state.finish()
        await message.reply("Создание бинго остановлено")
        return
    try:
        if is_hex_color(message.text) == True or is_const_color(message.text) == True:
            async with state.proxy() as data:
                data['background_theme_color'] = message.text
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add("2 цвета", "1 цвет")
            markup.add("Назад")
            await message.answer("🎨Выбери цветовую палитру", reply_markup=markup)
            await Form.color_palette.set()
        else:
            raise ValueError('Введи цвет в HEX формате или выбери кнопкой\n\nОзнакомиться с палитрой и получить цвет в формате HEX можно на сайте https://csscolor.ru или через поиск в браузере по запросу "HEX палитра"')
    except ValueError:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

        await message.reply('Введи цвет в HEX формате или выбери кнопкой\n\nОзнакомиться с палитрой и получить цвет в формате HEX можно на сайте https://csscolor.ru или через поиск в браузере по запросу "HEX палитра"', reply_markup=markup)
        return

@dp.message_handler(state=Form.color_palette)
async def get_color_palette(message: types.Message, state: FSMContext):
    if message.text == '/stop' or message.text == 'Назад':
        await state.finish()
        await message.reply("Создание бинго остановлено")
        return
    try:
        async with state.proxy() as data:
            if message.text == '2 цвета':
                data['color_palette'] = message.text
                await message.answer('Пришли 2 цвета через запятую с пробелом\nМожно вводить цвета в HEX формате\nПример: #faf3dd\n\nОзнакомиться с палитрой и получить цвет в формате HEX можно на сайте https://csscolor.ru или через поиск в браузере по запросу "HEX палитра"')
                await Form.two_colors.set()
            elif message.text == '1 цвет':
                data['color_palette'] = message.text
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
                #markup.add("brown", "pink", "purple", 'black')

                markup.add("Назад")
                await message.answer('🎨Выбери цвет либо введи свой!\nМожно вводить цвета в HEX формате\nПример: #faf3dd\n\nОзнакомиться с палитрой и получить цвет в формате HEX можно на сайте https://csscolor.ru или через поиск в браузере по запросу "HEX палитра"', reply_markup=markup)
                await Form.color_selection.set()
            else:
                raise ValueError("Выбери кнопкой 2 цвета или 1 цвет")
    except ValueError:
        await message.reply("Выбери кнопкой 2 цвета или 1 цвет")
        return

@dp.message_handler(state=Form.two_colors)
async def get_two_colors(message: types.Message, state: FSMContext):
    if message.text == '/stop' or message.text == 'Назад':
        await state.finish()
        await message.reply("Создание бинго остановлено")
        return
    try:
        colors = message.text.split(', ')
        if len(colors) == 1:
            raise ValueError("Введи 2 цвета в HEX формате через запятую")
        if (is_hex_color(colors[0]) == True or is_const_color(colors[0]) == True) and (is_hex_color(colors[1]) == True or is_const_color(colors[1]) and len(colors) == 2):
            async with state.proxy() as data:

                # При сохранении объекта в базу данных
                data['two_colors'] = pickle.dumps(message.text.split(', '))
                print(data['two_colors'])
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

                markup.add("Назад")
                await message.answer("Введите название бинго", reply_markup=markup)
                await Form.name_bingo.set()
        else:
            raise ValueError('Введи 2 цвета в HEX формате через запятую\n\nОзнакомиться с палитрой и получить цвет в формате HEX можно на сайте https://csscolor.ru или через поиск в браузере по запросу "HEX палитра"')
    except ValueError:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        await message.reply('Введи 2 цвета в HEX формате через запятую\n\nОзнакомиться с палитрой и получить цвет в формате HEX можно на сайте https://csscolor.ru или через поиск в браузере по запросу "HEX палитра"',  reply_markup=markup)
        return

@dp.message_handler(state=Form.color_selection)
async def get_color_selection(message: types.Message, state: FSMContext):
    if message.text == '/stop' or message.text == 'Назад':
        await state.finish()
        await message.reply("Создание бинго остановлено")
        return
    try:
        if is_hex_color(message.text) == True or is_const_color(message.text) == True:
                async with state.proxy() as data:
                    data['color_selection'] = message.text
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

                markup.add("Назад")
                await message.answer("Введите название бинго", reply_markup=markup)
                await Form.name_bingo.set()
        else:
            raise ValueError("Введи название цвета через запятую с пробелом")
    except ValueError:
        await message.reply("Введи название цвета через запятую с пробелом",  reply_markup=markup)
        return

@dp.message_handler(state=Form.name_bingo)
async def get_name_bingo(message: types.Message, state: FSMContext):
    if message.text == '/stop'or message.text == 'Назад':
        await state.finish()
        await message.reply("Создание бинго остановлено", reply_markup=menu_keyboard)
        return
    try:
        async with state.proxy() as data:
            data['name_bingo'] = message.text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

        create_text_image(message.text)
        photo = open('photo\\text_fonts_exemple.png', 'rb')
        await bot.send_photo(message.chat.id,  photo, caption='Вот так выглядит название бинго на разных шрифтах')
        markup.add("1", '2', "3", '4','5')
        markup.add("Назад")
        await message.answer("✍️ Выбери шрифт ", reply_markup=markup)
        await Form.font.set()
    except ValueError:
        await message.reply("Укажи название")
        return

@dp.message_handler(state=Form.font)
async def get_font(message: types.Message, state: FSMContext):
    if message.text == '/stop' or message.text == 'Назад':
        await state.finish()
        await message.reply("Создание бинго остановлено", reply_markup=menu_keyboard)
        return

    async with state.proxy() as data:
        data['font'] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Назад")
    await message.answer("Напиши слова для ячеек бинго через запятую\n\n😺 Не забудь про пробел после запятой!", reply_markup=markup)
    await Form.text_cells.set()

@dp.message_handler(state=Form.text_cells)
async def get_text_cells(message: types.Message, state: FSMContext):
    if message.text == '/stop' or message.text == 'Назад':
        await state.finish()
        await message.reply("Создание бинго остановлено", reply_markup=menu_keyboard)
        return
    try:
        async with state.proxy() as data:
            if (message.text.count(', ') + 1) == data['number_cells']**2:

                data['text_cells'] = message.text.split(', ')
                data['name_user'] = message.from_user.username
                data['approved_bingo'] = 0
                data['chat_id'] =  message.chat.id

                #if 'background_theme_photo' in data:
                #    with open(data['background_theme_photo'], 'rb') as file:
                #        # ваш код здесь
                #        background_theme_photo =
                #else:
                #    # код для обработки случая, когда фотография фона не выбрана
                #    background_theme_photo = 0
                #    print('NOT background_theme_photo')
            else:
                raise ValueError("Введи достаточное количество слов! \n\nEсли ты выбрал 3 количество то нужно 9 слов, 16 для 4, 25 для 5")
    except ValueError:
        await message.reply("Введи достаточное количество слов! \n\nEсли ты выбрал 3 количество то нужно 9 слов, 16 для 4, 25 для 5")
        return


    creature_new_bingo(data,  data['font'])
    user_id = message.from_user.id  # идентификатор пользователя, отправившего сообщение
    file_path = f"photo/{user_id}.png"  # путь к файлу которыйы удалим

    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Файл {file_path} удален")

    else:
        print(f"Файл {file_path} не существует")
    photo = types.InputFile('photo\\checkerboard.png')

    # Вставьте данные бинго в базу данных SQL
    if data['color_palette'] == '1 цвет':
        # открываем БД
        conn = sqlite3.connect('bingo_database.db')
        cursor = conn.cursor()
                        # Преобразуем фото в байты
        with open('photo\checkerboard.png', 'rb') as f:
            photo_bytes = f.read()
        cursor.execute('''INSERT INTO bingo_data
                      (name_user, number_cells, background_theme, background_theme_photo, color_palette,  color_selection, name_bingo, font, text_cells, approved_bingo, chat_id, bingo_photo)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (data['name_user'],
                    data['number_cells'],
                    data['background_theme'],
                    'background_theme_photo,', # background_theme_photo,
                    data['color_palette'],
                    data['color_selection'],
                    data['name_bingo'],
                    data['font'],
                    ', '.join(data['text_cells']),
                    data['approved_bingo'],
                    data['chat_id'],
                    photo_bytes

                    ))
        # Commit the changes and close the connection
        conn.commit()
        conn.close()

    elif data['color_palette'] == '2 цвета':
                # Преобразуем фото в байты
        with open('photo\checkerboard.png', 'rb') as f: ############################################################## ИЗМЕНИТЬ НА СОХРАНЕНИЕ ИЗ ДАТА
            photo_bytes = f.read()
        # открываем БД
        conn = sqlite3.connect('bingo_database.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO bingo_data
                      (name_user, number_cells, background_theme, background_theme_photo, color_palette, two_colors, name_bingo, font, text_cells, approved_bingo, chat_id, bingo_photo)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (data['name_user'],
                    data['number_cells'],
                    data['background_theme'],
                    'background_theme_photo,', # background_theme_photo,
                    data['color_palette'],
                    data['two_colors'],
                    data['name_bingo'],
                    data['font'],
                    ', '.join(data['text_cells']),
                    data['approved_bingo'],
                    data['chat_id'],
                    photo_bytes

                    ))
        #print(data)
        # Commit the changes and close the connection
        conn.commit()
        conn.close()

    # нужен ли обработчик


    await bot.send_photo(message.chat.id, photo, caption='Твое бинго создано!',reply_markup=menu_bingo_editor)
    #await bot.send_message(message.chat.id, f"Бинго создано: {data}")
    await state.finish()


#Хэндлеры создания бинго
def creating_bingo_handler(dp: Dispatcher):
    dp.register_message_handler(new_bingo, text=['🆕 Создать бинго','/new_bingo', ])
    dp.register_message_handler(get_number_cells, state=Form.number_cells)
    dp.register_message_handler(get_background_theme, state=Form.number_cells)
    dp.register_message_handler(get_color_palette, state=Form.color_palette)
    dp.register_message_handler(get_two_colors, state=Form.two_colors)
    dp.register_message_handler(get_color_selection, state=Form.color_selection)

    dp.register_message_handler(get_name_bingo, state=Form.name_bingo)
    dp.register_message_handler(get_font, state=Form.font)
    dp.register_message_handler(get_text_cells, state=Form.text_cells)

""" ПРОХОЖДЕНИЕ БИНГО
    1. получить id бинго
    2. получить список вопросов, количество ячеек
    3. получить фото бинго
    4. через состояние начать этап прохождения бинго
    5. прислать пользователю сообщение в котором вопрос и фото бинго а внизу клавиатура с кнопками да нет
        если пользователь нажал да то ячейка на фото
    сделать третью таблицу с данными какие бинго прошел пользователь и его результатами"""