from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from keyboards import *
from states import *
from functions import *
from aiogram import Dispatcher, types
from create_bot import bot, dp
from PIL import Image, ImageDraw, ImageFont
from test_game_bingo import *

# Обработчик команды /start с аргументами для загрузки бинго из базы данных


class PassBingoForStart(StatesGroup):
    waiting_for_start_decision = State()
    passing = State()

answers = {}
photo_fon = 0

async def send_welcome(message: types.Message, state: FSMContext):
    args = message.get_args()
    if not args:
        await message.reply("Привет Я помогу тебе легко создавать бинго\n\n/new_bingo - создать бинго\n/stop - остановить создание бинго\n/help - загляни туда чтобы узнать больше", reply_markup=menu_keyboard)
    else:
        bingo_id = int(args)
        photo = get_bingo_photo(bingo_id)

        if photo is None:
            await message.answer('Бинго не найдено')
            return
        # Отправка сообщения с бинго
        #await bot.send_photo(message.chat.id, photo=photo, reply_markup=bingo_my_selection_keyboard)
        await send_game_bingo_command(message, state, bingo_id)


#@dp.message_handler(text=['/menu', 'Меню'])
async def send_menu(message: types.Message):
    await message.reply("Главное меню", reply_markup=menu_keyboard)

#@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    photo = open('photo\color_help.png', 'rb')
    # обновить пути ко всем фото
    await bot.send_photo(message.chat.id,  photo, caption='тут будет информация о боте и командах', reply_markup=menu_keyboard)

#@dp.message_handler(text=['/admin', 'админ', 'Админ'])
async def send_admin(message: types.Message):
    user_name = message.from_user.id
    if is_user_admin(user_name):
        await message.reply("Админ панель", reply_markup=admin_keyboard)
    else:
        await message.reply("Упс, ты не админ")


# Регистрируем хэндлер для обработки нажатий на кнопки в состоянии 'waiting_for_action'
@dp.message_handler(state=PassBingoForStart.waiting_for_start_decision)
async def process_bingo_action_handler(message: types.Message, state: FSMContext):
    await process_game_bingo_action(message, state)

# Регистрируем хэндлер для обработки нажатий на кнопки в состоянии 'passing'
@dp.message_handler(state=PassBingoForStart.passing)
async def process_answer_handler(message: types.Message, state: FSMContext):
    await process_game_answer(message, state)



def register_message_main_handler(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start'])
    dp.register_message_handler(send_menu, text=['/menu', 'Меню'])
    dp.register_message_handler(send_help, commands=['help'])
    dp.register_message_handler(send_admin, text=['/admin', 'админ', 'Админ'])