
from aiogram       import  Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
storage = MemoryStorage()
API_TOKEN = '6805806834:AAExF13Nn4QwVjmZN_5CPE-_Yt8OwKiR1so'
bot = Bot(token=API_TOKEN, parse_mode='HTML')#, parse_mode='MarkdownV2'
dp = Dispatcher(bot, storage=storage)