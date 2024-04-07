@dp.message_handler(commands=['check_bingo'])
async def start(message: types.Message):
    # Получаем данные, где approved_bingo == 0
    data = get_data_from_database()

    # Создаем экземпляр клавиатуры
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    # Добавляем кнопки на клавиатуру
    button_approve = KeyboardButton("Одобрить")
    button_reject = KeyboardButton("Не одобрить")
    button_ban = KeyboardButton("Забанить")
    keyboard.add(button_approve, button_reject, button_ban)

    # Отправляем первое сообщение с клавиатурой
    if data:
        item = data[0]
        text = f"Номер бинго: {item[0]}\nНазвание: {item[1]}\nСоздатель: {item[2]}\nСостояние: {item[3]}"
        await message.answer(text, reply_markup=keyboard)

    # Ожидаем ответа пользователя
    response = await dp.wait_for_response(timeout=60.0)

    # Цикл для обработки всех сообщений в базе данных
    for item in data:
        if response and response.message:
            # Обновляем approved_bingo в зависимости от ответа пользователя
            if response.message.text.lower() == "одобрить":
                item[3] = 1
            elif response.message.text.lower() == "не одобрить":
                item[3] = 0
            elif response.message.text.lower() == "забанить":
                item[3] = 2

            # Обновляем данные в базе данных
            update_data_in_database(item)

            # Отправляем следующее сообщение с клавиатурой
            text = f"Номер бинго: {item[0]}\nНазвание: {item[1]}\nСоздатель: {item[2]}\nСостояние: {item[3]}"
            await message.answer(text, reply_markup=keyboard)

            # Ожидаем ответа пользователя
            response = await dp.wait_for_response(timeout=60.0)

    # Отправляем сообщение о том, что все данные обработаны
    await message.answer("Все данные обработаны.", reply_markup=ReplyKeyboardRemove())



def get_data_from_database():
    conn = sqlite3.connect('bingo_database.db')  # Подключение к базе данных SQLite
    cursor = conn.cursor()

    # Выполнение SQL-запроса для получения данных, где approved_bingo == 0
    cursor.execute("SELECT id, name_bingo, name_user, approved_bingo FROM bingo_data WHERE approved_bingo = 0")
    data = cursor.fetchall()

    conn.close()  # Закрытие соединения с базой данных

    return data


def update_data_in_database(name_bingo, name_user):
    conn = sqlite3.connect('bingo_database.db')  # Подключение к базе данных SQLite
    cursor = conn.cursor()

    # Выполнение SQL-запроса для добавления данных в таблицу bingo_data
    cursor.execute("INSERT INTO bingo_data (name_bingo, name_user, approved_bingo) VALUES (?, ?, ?)", (name_bingo, name_user, 0))

    conn.commit()  # Применение изменений
    conn.close()  # Закрытие соединения с базой данных
