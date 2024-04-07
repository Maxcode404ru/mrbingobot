from keyboards     import menu_keyboard, admin_keyboard

from aiogram.utils import executor
import logging
import asyncio

from create_bot import bot, dp


logging.basicConfig(level=logging.INFO)
from handlers import admin_panel, main_hendlers, additional_handlers, creating_bingo_handler


admin_panel.register_handlers_admin_panel(dp)
main_hendlers.register_message_main_handler(dp)
additional_handlers.register_message_additional_handlers(dp)
#creating_bingo_handler.register_message_main_handler(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
