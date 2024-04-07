from aiogram.dispatcher.filters.state import State, StatesGroup

# Создаем машину состояний
class AddAdminState(StatesGroup):
    waiting_for_admin_name = State()

# Создаем машину состояний
class DeleteAdminState(StatesGroup):
    waiting_for_admin_id = State()

# Создаем машину состояний
class ApproveBingo(StatesGroup):
    waiting_for_decision = State()

# Создаем машину состояний
class CheckBingo(StatesGroup):
    waiting_for_answer = State()

# Состояние команды /bingo
class BingoStates(StatesGroup):
    waiting_for_action = State()

class Form(StatesGroup):
    number_cells = State()
    background_theme = State()
    background_theme_photo = State()
    background_theme_color = State()
    color_palette = State()
    two_colors = State()
    color_selection = State()
    name_bingo = State()
    font = State()
    text_cells = State()
    completion_bingo = State()

"""

ГЛАВНЫЕ ПЕРЕМЕННЫЕ И ЗНАЧЕНИЯ


имя создателя
количество ячеек
тема фона
фото фона или цвет фона
цветовая палитра
2 цвета или один
имя бинго
цвет имяни бинго
шрифт текстов
текст ячеек

name_user,
number_cells ,
background_theme ,
background_theme_photo ,
color_palette ,
two_colors ,
color_selection ,
name_bingo ,
font ,
text_cells




"""