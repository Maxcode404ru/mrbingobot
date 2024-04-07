
from aiogram       import  Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
storage = MemoryStorage()
API_TOKEN = '7050336028:AAFtLJZ052g9M8pWMuNxNKAEI1jJp9smB3U'
bot = Bot(token=API_TOKEN, parse_mode='HTML')#, parse_mode='MarkdownV2'
dp = Dispatcher(bot, storage=storage)