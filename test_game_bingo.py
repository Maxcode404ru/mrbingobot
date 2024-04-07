from keyboards import *
from text_fonts_exemple import *
from states import *
import sqlite3
from io import BytesIO
import random
from functions import *
from create_bot import bot, dp
from aiogram import  types, Dispatcher

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from aiogram.dispatcher.filters.state import State, StatesGroup

class PassBingoForStart(StatesGroup):
    waiting_for_start_decision = State()
    passing = State()

answers = {}
photo_fon = 0

async def send_game_bingo_command(message: types.Message, state: FSMContext, bingo_id):
    conn = sqlite3.connect('bingo_database.db')
    cursor = conn.cursor()

    # Store the selected bingo ID in the state
    async with state.proxy() as data:
        data['bingo_id'] = bingo_id

        # Выполняем SQL-запрос для получения number_cells из базы данных по её идентификатору
        cursor.execute("SELECT number_cells, bingo_photo FROM bingo_data WHERE id=?", (bingo_id,))
        result = cursor.fetchone()
        if result is None:
            await message.answer('Бинго не найдено')
            return

        data['number_cells'] = result[0]
        data['photo'] = BytesIO(result[1])

    # Закрываем соединение с базой данных
    conn.close()

    # Send the photo
    await bot.send_photo(message.chat.id, photo=data['photo'], reply_markup=bingo_share_keyboard)

    # Set the state to 'waiting_for_action'
    await PassBingoForStart.waiting_for_start_decision.set()

async def process_game_bingo_action(message: types.Message, state: FSMContext):
    print('РАБОТАЕТ !!!')
    if message.text == '/stop' or message.text == 'Назад':
        await message.reply("Процесс остновлен", reply_markup=menu_keyboard)
        await state.finish()
    elif message.text == '❌ Следующее бинго':
        #bingo_id = await get_next_bingo_id()
        #if bingo_id is None:
        #    await message.answer('Бинго не найдено')
        #    return
        await send_game_bingo_command(message, state, bingo_id)
    elif message.text == '✅ Пройти бинго':
        # Get the selected bingo data
        async with state.proxy() as data:
            bingo_id = data.get('bingo_id')
        text_cells = get_bingo_data(bingo_id)

        if text_cells is None:
            await message.answer('Bingo data not found.')
            return

        # Store the bingo data in the state
        async with state.proxy() as data:
            data['text_cells'] = text_cells
            data['current_question'] = 0

        # Reset the global answers dictionary for each game of bingo
        global answers
        answers = {}

        # Set the state to 'passing'
        await PassBingoForStart.passing.set()

        # Ask the next question
        question_text, current_question = await ask_next_question(message, state)

async def process_game_answer(message: types.Message, state: FSMContext):
    if message.text == '/stop' or message.text == 'Назад':
        await message.reply("Процесс остновлен", reply_markup=menu_keyboard)
        await state.finish()
    async with state.proxy() as data:
        if 'current_question' not in data:
                #await message.reply("Бинго не запущено. Начните новую игру.", reply_markup=menu_keyboard)
                await state.finish()
                return
    async with state.proxy() as data:
        current_question = data['current_question']  # Текущий вопрос
        text_cells = data['text_cells']  # Текстовые ячейки
        number_cells = data['number_cells'] # Количество ячеек
        photo = data['photo']  # Фотография

    # Сохраняем фотографию во временный файл
    with open('temp_image.jpg', 'wb') as f:
        f.write(photo.getvalue())

    # Открываем временный файл и рисуем на нем
    img = Image.open('temp_image.jpg')

    # Преобразуем основное изображение в формат, поддерживающий прозрачность (RGBA), если это еще не сделано
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    draw = ImageDraw.Draw(img)

    if message.text == '✅':
        answers[current_question] = True
        text_cells[current_question] = '✅'

        if number_cells == 5:
            print(number_cells)
            cell_size_x = 150 # Ширина
            cell_size_y = 150 # Высота
            board_offset_x = 150
            board_offset_y = 250
            cell_padding = 10 # Отступ от квадратов
        if number_cells == 4 or number_cells == '4':
            print(number_cells)
            cell_size_x = 180
            cell_size_y = 180
            board_offset_x = 150
            board_offset_y = 250
            cell_padding = 20 # Отступ от квадратов
        if number_cells == 3:
            print(number_cells)
            cell_size_x = 250
            cell_size_y = 250
            board_offset_x = 150
            board_offset_y = 250
            cell_padding = 30 # Отступ от квадратов

        # Вычисляем позицию ячейки с отступом
        cell_x = current_question % number_cells
        cell_y = current_question // number_cells
        x1 = cell_x * (cell_size_x + cell_padding) + board_offset_x
        y1 = cell_y * (cell_size_y + cell_padding) + board_offset_y
        x2 = x1 + cell_size_x
        y2 = y1 + cell_size_y
        cell_position = (x1, y1, x2, y2)
        print('ВЫЧИСЛЯЕМ')
        print(cell_padding)

        # Открываем фото, изменяем размеры и делаем его полупрозрачным
        photo = Image.open('photo\photo_putty.png')

        # Преобразуем фото в формат, поддерживающий прозрачность (RGBA), если это еще не сделано
        if photo.mode != 'RGBA':
            photo = photo.convert('RGBA')

        photo = photo.resize((cell_size_x, cell_size_y))

        # Создаем новый альфа-канал с нужной прозрачностью (128 соответствует 50% прозрачности)
        new_alpha = Image.new('L', photo.size, 128)

        # Заменяем альфа-канал фото на новый
        photo.putalpha(new_alpha)

        # Вставляем фото на основное изображение
        img.paste(photo, cell_position, mask=new_alpha)

    elif message.text == '❌':
        answers[current_question] = False
        text_cells[current_question] = '❌'

    else:
        await message.answer('Используй кнопки для выбора ответа')
        return

    # Сохраняем измененное изображение в объект BytesIO
    new_photo_bytes = BytesIO()
    img.save(new_photo_bytes, 'PNG')
    new_photo_bytes.seek(0)

    # Обновляем фотографию в состоянии
    async with state.proxy() as data:
        data['photo'] = new_photo_bytes

    if data['current_question'] == len(data['text_cells']) - 1:
        # Это был последний вопрос, вычисляем количество правильных ответов
        yes_count = sum(value for value in answers.values() if value == True)
        yes_count = yes_count * 100 // len(data['text_cells'])
        await bot.send_photo(message.chat.id, photo=data['photo'], caption=f'Твой результат <b>{yes_count}</b> % бинго поподаний!', reply_markup=menu_keyboard)

        await state.finish()
    else:
        # Увеличиваем счетчик текущего вопроса
        async with state.proxy() as data:
            data['current_question'] += 1

        # Задаем следующий вопрос
        question_text, current_question = await ask_next_question(message, state)

async def ask_next_question(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        current_question = data['current_question']
        text_cells = data['text_cells']

    # Ask the next question
    question_text = text_cells[current_question]

    # Send the photo
    await bot.send_photo(message.chat.id, photo=data['photo'], caption=f'Вопрос {current_question + 1}: <b>{question_text}</b>\nВыбери кнопкой ✅ или ❌', reply_markup=bingo_passing_keyboard)

    return question_text, current_question