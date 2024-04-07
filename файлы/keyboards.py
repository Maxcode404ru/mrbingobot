from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# создаем клавиатуру меню
menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton('🆕Создать бинго')
button2 = KeyboardButton('🌟Бинго')
button3 = KeyboardButton('👤Мои бинго')
button4 = KeyboardButton('❤️PRO-аккаунт')

menu_keyboard.add(button1, button2, button3, button4)


# создаем клавиатуру редактирования бинго
menu_bingo_editor = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton('🆕Создать бинго')
button2 = KeyboardButton('Изменить название')
button3 = KeyboardButton('Изменить текст')
button4 = KeyboardButton('Изменить фон')
button5 = KeyboardButton('Изменить шрифт')
button6 = KeyboardButton('Изменить цвет названия')
button7 = KeyboardButton('Изменить цвет текста')
button8 = KeyboardButton('Изменить цвет ячеек')
button9 = KeyboardButton('Меню')

menu_bingo_editor.add(button1, button2, button3, button4, button5, button6, button7, button8, button9)


# создаем клавиатуру Админ панели
admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton('Добавить админа')
button2 = KeyboardButton('Удалить админа')
button_list_admins = KeyboardButton("Список админов")
watch_bingo = KeyboardButton("Проверить бинго")
check_bingo = KeyboardButton("Одобрить бинго")

admin_keyboard.row(button1, button2)
admin_keyboard.add(button_list_admins)
admin_keyboard.add(watch_bingo)
admin_keyboard.add(check_bingo)





# Создаем экземпляр клавиатуры выбора (перед прохождением) бинго
bingo_selection_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
button_approve = KeyboardButton("✅ Пройти бинго")
button_reject = KeyboardButton("❌ Следующее бинго")

bingo_selection_keyboard.add(button_approve, button_reject)


# Создаем экземпляр клавиатуры прохождения бинго
bingo_passing_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
button_approve = KeyboardButton("✅")
button_reject = KeyboardButton("❌")

bingo_passing_keyboard.add(button_approve, button_reject)


# Создаем экземпляр клавиатуры для проверки бинго админом (Удаления)
admin_bingo_selection_keyboard  = ReplyKeyboardMarkup(resize_keyboard=True)
button_approve = KeyboardButton("✅ Оставим, следующее бинго")
button_reject = KeyboardButton("❌ Удаляем бинго")

admin_bingo_selection_keyboard.add(button_approve, button_reject)


# Создаем экземпляр клавиатуры для одобрения бинго админом (Одобрения)
check_bingo_selection_keyboard  = ReplyKeyboardMarkup(resize_keyboard=True)
button_approve = KeyboardButton("✅ Одообрено")
button_reject = KeyboardButton("❌ Не одобрено")

check_bingo_selection_keyboard.add(button_approve, button_reject)
