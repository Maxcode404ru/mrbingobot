"""from keyboards import *
from text_fonts_exemple import *
from states import *
import sqlite3
from io import BytesIO
import random
from functions import *
from create_bot import bot, dp
from aiogram import types, Dispatcher

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

storage = MemoryStorage()

class BingoProcessStates(StatesGroup):
    asking_question = State()

class BingoStates(StatesGroup):
    waiting_for_action = State()

async def start_bingo_process(message: types.Message):
    # Получите фотографию бинго, имя и текстовые ячейки здесь (например, из базы данных или другого источника)
    # Например:
    bingo_photo = ...
    bingo_name = ...
    text_cells = [..., ..., ...]  # List of text cells

    # Set the state to 'asking_question'
    await BingoProcessStates.asking_question.set()

    # Store the bingo data in the state
    async with FSMContext.proxy() as data:
        data['bingo_photo'] = bingo_photo
        data['bingo_name'] = bingo_name
        data['text_cells'] = text_cells
        data['selected_cells'] = {}
        data['score'] = 0
        data['current_question'] = 0

    # Start asking questions
    await ask_next_question(message)

@dp.message_handler(state=BingoProcessStates.asking_question)
async def process_user_answer(message: types.Message, state: FSMContext):
    if message.text.lower() in ['да', 'yes', 'y']:
        async with state.proxy() as data:
            data['selected_cells'][data['current_question']] = True
            data['score'] += 1
    elif message.text.lower() in ['нет', 'no', 'n']:
        async with state.proxy() as data:
            data['selected_cells'][data['current_question']] = False

    # Check if there are more questions
    if len(data['text_cells']) > data['current_question'] + 1:
        data['current_question'] += 1
        await ask_next_question(message)
    else:
        # Calculate the final score
        async with state.proxy() as data:
            final_score = data['score']

        # Clear the state
        await state.finish()

        # Send the final result to the user
        await message.answer(f'Вы прошли бинго и набрали {final_score} баллов!')

async def ask_next_question(message: types.Message):
    async with FSMContext.proxy() as data:
        current_question = data['current_question']
        question_text = data['text_cells'][current_question]

    # Ask the question
    await message.answer(f'Вопрос {current_question + 1}: {question_text}\nОтветьте "Да" или "Нет"')

@dp.message_handler(commands=['bingo'])
async def send_bingo_command(message: types.Message):
    conn = sqlite3.connect('bingo_database.db')
    cursor = conn.cursor()
    # Выполнение SQL-запроса для получения всех id из таблицы bingo_data
    cursor.execute("SELECT id FROM bingo_data")
    ids = cursor.fetchall()
    # Преобразование списка кортежей в список целых чисел
    ids = [id[0] for id in ids]
    # Выбор случайного id из списка
    random_id = random.choice(ids)
    # Выполняем SQL-запрос для получения фотографии из базы данных по её идентификатору
    cursor.execute("SELECT bingo_photo FROM bingo_data WHERE id=?", (random_id,))
    result = cursor.fetchone()
    # Закрываем соединение с базой данных
    conn.close()
    # Проверяем, что фотография существует в базе данных
    if result is None:
        await message.answer('Фотография не найдена')
        return

   # Установите состояние в 'waiting_for_action'
    await BingoStates.waiting_for_action.set()

    # Преобразуем фотографию в формат, подходящий для отправки в Telegram
    photo = BytesIO(result[0])
    photo.name = 'photo.jpg'

    # Send the photo
    await bot.send_photo(message.chat.id, photo=photo, reply_markup=bingo_selection_keyboard)

    # Зарегистрируйте следующий обработчик для обработки действия пользователя
    dp.register_message_handler(process_bingo_action, state=BingoStates.waiting_for_action)

@dp.message_handler(state=BingoStates.waiting_for_action)
async def process_bingo_action(message: types.Message, state: FSMContext):
    if message.text == '❌ Следующее бинго':
        await send_bingo_command(message)
    elif message.text == '✅ Пройти бинго':
        # Here, you can start the bingo process
        await start_bingo_process(message)
    else:
        await message.answer('Выббери действие нажав на кнопку')

    # Clear the state after processing the action
    await state.finish()

@dp.message_handler(commands=['start_bingo'])
async def start_bingo_command(message: types.Message):
    # Get the bingo data here (e.g., from the database or another source)
    # Then call the start_bingo_process function
    await start_bingo_process(message)

setup_database_result_bingo()
"""