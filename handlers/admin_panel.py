import sqlite3
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message
from keyboards import *
from states import *
from aiogram.types import ReplyKeyboardRemove
from functions import *
from aiogram import Dispatcher, types
from io import BytesIO
import random
from create_bot import bot, dp
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import StateFilter

class CheckBingo(StatesGroup):
    # ... other states, if any ...
    waiting_for_decision = State()
    waiting_for_answer = State()

# Создаем соединение с базой данных
conn = sqlite3.connect('database.db')
# Создаем курсор
cursor = conn.cursor()
# Выполняем SQL-запрос на создание таблицы, если она еще не существует
cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin_data (
        chat_id INTEGER,
        admin_id TEXT
    );
''')
# Фиксируем изменения
conn.commit()
# Закрываем курсор
cursor.close()

# Создаем хранилище для состояний
storage = MemoryStorage()




# Создаем хендлер для добавления админа
#@dp.message_handler(text=['/add_admin', 'Добавить админа', 'добавить админа'])
async def add_admin_start(message: types.Message, state: FSMContext):
    if message.text == '/stop' or message.text == 'Назад':
        await message.reply("Процесс остановлен")
        # Сбрасываем состояние
        await state.finish()
    else:
        user_name = message.from_user.id
        print(user_name)
        if is_user_admin(user_name):
            # Отправляем сообщение пользователю с просьбой ввести ник админа
            await message.answer('Введи Айди будущего админа:\nон выглядит как код\n\nЕсли ты передумал нажми /stop')
            # Переводим пользователя в состояние ожидания ввода ника админа
            await AddAdminState.waiting_for_admin_name.set()
        else:
            await message.reply("Упс, ты не админ")

# Создаем хендлер для обработки ввода ника админа
@dp.message_handler(state=AddAdminState.waiting_for_admin_name)
async def add_admin_name(message: types.Message, state: FSMContext):
    if message.text == '/stop' or message.text == 'Назад':
        await message.reply("Процесс остановлен")
        # Сбрасываем состояние
        await state.finish()
    else:
        # Получаем ник админа из сообщения пользователя
        admin_id = message.text

        # Добавляем ник админа в базу данных админов
        conn = sqlite3.connect('bingo_database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO admin_data (admin_id) VALUES (?)', (admin_id,))
        conn.commit()
        conn.close()

        # Отправляем сообщение пользователю о том, что админ успешно добавлен
        await message.answer(f'Админ {admin_id} успешно добавлен')

        # Сбрасываем состояние
        await state.finish()



#@dp.message_handler(text=['/delete_admin', 'Удалить админа', 'удалить админа'])
async def delete_admin_start(message: types.Message, state: FSMContext):
    if message.text == '/stop' or message.text == 'Назад':
        await message.reply("Процесс остановлен")
        # Сбрасываем состояние
        await state.finish()
    else:
        user_name = message.from_user.id
        print(user_name)
        if is_user_admin(user_name):
            await message.answer('Введи @Ник_айди админа, которого хочешь удалить:\nвводи без @\n\nЕсли ты передумал нажми /stop')

            #Переводим пользователя в состояние ожидания ввода ника админа
            await DeleteAdminState.waiting_for_admin_id.set()
        else:
            await message.reply("Упс, ты не админ")
#Создаем хендлер для обработки ввода id админа
@dp.message_handler(state=DeleteAdminState.waiting_for_admin_id)
async def delete_admin_id(message: types.Message, state: FSMContext):
    if message.text == '/stop' or message.text == 'Назад':
        await message.reply("Процесс остановлен")
        # Сбрасываем состояние
        await state.finish()
    else:
        admin_id = message.text
        # Удаляем id админа из базы данных админов
        conn = sqlite3.connect('bingo_database.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM admin_data WHERE admin_id = ?', (admin_id,))
        conn.commit()
        conn.close()

        # Отправляем сообщение пользователю о том, что админ успешно удален
        await message.answer(f'Админ {admin_id} успешно удален!')

        # Сбрасываем состояние
        await state.finish()



#@dp.message_handler(text=['/get_admins', 'Список админов', 'список админов'])
async def get_admins(message: types.Message):
    user_name = message.from_user.id
    print(user_name)
    if is_user_admin(user_name):
        # Получаем список админов из базы данных
        conn = sqlite3.connect('bingo_database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT admin_id FROM admin_data')
        admins = cursor.fetchall()
        conn.close()

        # Форматируем список админов в виде строки
        admins_list = '\n'.join([admin[0] for admin in admins])

        # Отправляем список админов в виде сообщения
        await message.answer(f'Список админов:\n{admins_list}')
    else:
        await message.reply("Упс, ты не админ")



# Создаем машину состояний
class WatchBingo(StatesGroup):
    waiting_for_decision = State()



# Состояние для хранения текущего ID бинго
current_bingo_id = None




def register_handlers_admin_panel(dp: Dispatcher):
    dp.register_message_handler(add_admin_start, text=['/add_admin', 'Добавить админа', 'добавить админа'])

    dp.register_message_handler(send_admin_bingo_command, text=['/watch_bingo', 'Проверить бинго'])
    dp.register_message_handler(process_admin_bingo_action, state = AdminBingoStates.waiting_for_admin_action)

    dp.register_message_handler(check_bingo_command, text=['/check_bingo', 'Одобрить бинго'])
    dp.register_message_handler(process_check_bingo_action, state=AdminCheckBingoStates.waiting_for_admin_check)
    dp.register_message_handler(delete_admin_start,text=['/delete_admin', 'Удалить админа', 'удалить админа'])
    dp.register_message_handler(get_admins,text=['/get_admins', 'Список админов', 'список админов'])


class AdminBingoStates(StatesGroup):
    waiting_for_admin_action = State()

class AdminPassBingo(StatesGroup):

    passing = State()

class AdminCheckBingoStates(StatesGroup):
    waiting_for_admin_check = State()



# watch_bingo
async def send_admin_bingo_command(message: types.Message, state: FSMContext):
    conn = sqlite3.connect('bingo_database.db')
    cursor = conn.cursor()

    # Выполняем SQL-запрос для получения всех id из таблицы bingo_data, где approved_bingo равен 1
    cursor.execute("SELECT id FROM bingo_data WHERE approved_bingo=1")
    ids = cursor.fetchall()

    # Преобразование списка кортежей в список целых чисел
    ids = [id[0] for id in ids]
    if not ids:
        await message.answer('Бинго кончились 0 бинго в общем доступе')
        await state.finish()
        return
    # Выбор случайного id из списка
    random_id = random.choice(ids)

    # Выполняем SQL-запрос для получения фотографии из базы данных по её идентификатору
    cursor.execute("SELECT bingo_photo FROM bingo_data WHERE id=?", (random_id,))
    result = cursor.fetchone()

    # Проверяем, что фотография существует в базе данных
    if result is None:
        await message.answer('Фотография не найдена')
        return

    # Преобразуем фотографию в формат, подходящий для отправки в Telegram
    photo = BytesIO(result[0])
    photo.name = 'photo.jpg'

    # Установите состояние в 'waiting_for_admin_action'
    await AdminBingoStates.waiting_for_admin_action.set()

    # Store the selected bingo ID in the state
    async with state.proxy() as data:
        data['bingo_id'] = random_id
        data['photo'] = photo
        # Выполняем SQL-запрос для получения number_cells из базы данных по её идентификатору
        cursor.execute("SELECT number_cells FROM bingo_data WHERE id=?", (random_id,))
        data['number_cells'] =  cursor.fetchone()
        # Закрываем соединение с базой данных
        conn.close()

    # Send the photo
    await bot.send_photo(message.chat.id, photo=photo,caption='Процессдля удаления устаревших бинго\n\n<b>Оставляем или удаляем?</b>', reply_markup=admin_bingo_selection_keyboard)

    # Set the state to 'waiting_for_admin_action'
    await AdminBingoStates.waiting_for_admin_action.set()

async def process_admin_bingo_action(message: types.Message, state: FSMContext):
    if message.text == '/stop' or message.text == 'Назад':
        await message.answer('Процесс остановлен', reply_markup=menu_keyboard)
        await state.finish()
    elif message.text == '❌ Удаляем бинго':
        print('❌ Удаляем бинго')
        # Получаем выбранные данные бинго
        async with state.proxy() as data:
            bingo_id = data.get('bingo_id')

        # Обновляем approved_bingo на 4 в базе данных
        conn = sqlite3.connect('bingo_database.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE bingo_data SET approved_bingo=4 WHERE id=?", (bingo_id,))
        conn.commit()
        conn.close()

        # Отправляем следующее бинго администратору
        await send_admin_bingo_command(message, state)
    elif message.text == '✅ Оставим, следующее бинго':
        print('✅ Оставим, следующее бинго')
        # Отправляем следующее бинго администратору
        await send_admin_bingo_command(message, state)


# check_bingo
async def check_bingo_command(message: types.Message, state: FSMContext):
    conn = sqlite3.connect('bingo_database.db')
    cursor = conn.cursor()

    # Выполняем SQL-запрос для получения всех id из таблицы bingo_data, где approved_bingo равен 0
    cursor.execute("SELECT id FROM bingo_data WHERE approved_bingo=0")
    ids = cursor.fetchall()

    # Преобразование списка кортежей в список целых чисел
    ids = [id[0] for id in ids]
    if not ids:
        await message.answer('Больше нет запросов на добавление бинго')
        await state.finish()
        return
    # Выбор случайного id из списка
    random_id = random.choice(ids)

    # Выполняем SQL-запрос для получения фотографии из базы данных по её идентификатору
    cursor.execute("SELECT bingo_photo FROM bingo_data WHERE id=?", (random_id,))
    result = cursor.fetchone()

    # Проверяем, что фотография существует в базе данных
    if result is None:
        await message.answer('Фотография не найдена')
        return

    # Преобразуем фотографию в формат, подходящий для отправки в Telegram
    photo = BytesIO(result[0])
    photo.name = 'photo.jpg'

    # Установите состояние в 'waiting_for_admin_pass'
    await AdminPassBingo.passing.set()

    # Store the selected bingo ID in the state
    async with state.proxy() as data:
        data['bingo_id'] = random_id
        data['photo'] = photo
        # Выполняем SQL-запрос для получения number_cells из базы данных по её идентификатору
        cursor.execute("SELECT number_cells FROM bingo_data WHERE id=?", (random_id,))
        data['number_cells'] =  cursor.fetchone()
        # Закрываем соединение с базой данных
        conn.close()

    # Send the photo
    await bot.send_photo(message.chat.id, photo=photo,caption='Процесс для добавления бинго в общий доступ\n\n<b>Одобрить или не одобрить?</b>', reply_markup=check_bingo_selection_keyboard)

    # Set the state to 'waiting_for_admin_check'
    await AdminCheckBingoStates.waiting_for_admin_check.set()


async def process_check_bingo_action(message: types.Message, state: FSMContext):
    print('REA')
    if message.text == '/stop' or message.text == 'Назад':
        await message.answer('Процесс остановлен', reply_markup=menu_keyboard)
        await state.finish()
    elif message.text == '❌ Не одобрено':
        async with state.proxy() as data:
            bingo_id = data.get('bingo_id')

        conn = sqlite3.connect('bingo_database.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE bingo_data SET approved_bingo=2 WHERE id=?", (bingo_id,))
        conn.commit()
        conn.close()

        # Устанавливаем состояние 'waiting_for_admin_approval'
        await AdminCheckBingoStates.waiting_for_admin_check.set()

        # Отправляем следующее бинго администратору
        await check_bingo_command(message, state)
    elif message.text == '✅ Одобрено':
        async with state.proxy() as data:
            bingo_id = data.get('bingo_id')

        conn = sqlite3.connect('bingo_database.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE bingo_data SET approved_bingo=1 WHERE id=?", (bingo_id,))
        conn.commit()
        conn.close()

        # Устанавливаем состояние 'waiting_for_admin_approval'
        await AdminCheckBingoStates.waiting_for_admin_check.set()

        # Отправляем следующее бинго администратору
        await check_bingo_command(message, state)
