
from aiogram import types
from keyboards import *
from states import *
from functions import *
from aiogram import Dispatcher, types
from create_bot import bot, dp


#@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет Я помогу тебе легко создавать бинго\n\n/new_bingo - создать бинго\n/stop - остановить создание бинго\n/help - загляни туда чтобы узнать больше", reply_markup=menu_keyboard)
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
    user_name = message.from_user.username
    if is_user_admin(user_name):
        await message.reply("Админ панель", reply_markup=admin_keyboard)
    else:
        await message.reply("Упс, ты не админ")

def register_message_main_handler(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start'])
    dp.register_message_handler(send_menu, text=['/menu', 'Меню'])
    dp.register_message_handler(send_help, commands=['help'])
    dp.register_message_handler(send_admin, text=['/admin', 'админ', 'Админ'])