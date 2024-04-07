from PIL import Image, ImageDraw, ImageFont

# Создаем изображение размером 1000x1000 пикселей
img = Image.new('RGB', (1000, 1000), color='white')

# Создаем объект ImageDraw для рисования на изображении
draw = ImageDraw.Draw(img)

# Задаем шрифт и цвет текста
font_info = ImageFont.truetype('fonts\Caveat-Bold.ttf', 50)
text_color_name = 'white'
text_color_info = 'white'

# Рисуем текст на изображении
name_bingo = 'Мое бинго'
draw.text((410, 100), name_bingo, font=font_info, fill=text_color_name, stroke_width=5, stroke_fill='black')
draw.text((340, 150), 'Создано tg: @BibingoBot ', font=font_info, fill=text_color_info, stroke_width=5, stroke_fill='black')

# Сохраняем изображение в файл
img.save('bingo.png')




async def send_bingo_my_command(message: types.Message, state: FSMContext):
    conn = sqlite3.connect('bingo_database.db')
    cursor = conn.cursor()
    # Получение user_id из объекта сообщения
    user_id = message.from_user.id
    # Выполнение SQL-запроса для получения всех id из таблицы bingo_data, где chat_id и user_id совпадают с чатом и id пользователя
    cursor.execute("SELECT id FROM bingo_data WHERE chat_id=? AND user_id=?", (message.chat.id, user_id))
    ids = cursor.fetchall()
    # Преобразование списка кортежей в список целых чисел
    ids = [id[0] for id in ids]
    # Выбор случайного id из списка
    random_id = random.choice(ids) if ids else None
    # Выполнение SQL-запроса для получения фотографии из базы данных по её идентификатору
    if random_id:
        cursor.execute("SELECT bingo_photo FROM bingo_data WHERE id=?", (random_id,))
        result = cursor.fetchone()
        # Проверка, что фотография существует в базе данных
        if result is None:
            await message.answer('Фотография не найдена')
            return
        # Преобразование фотографии в формат, подходящий для отправки в Telegram
        photo = BytesIO(result[0])
        photo.name = 'photo.jpg'
        global photo_fon
        photo_fon = photo
        # Установка состояния в 'waiting_for_action'
        await BingoStates.waiting_for_action.set()
        # Сохранение выбранного идентификатора бинго в состоянии
        async with state.proxy() as data:
            data['bingo_id'] = random_id
            data['photo'] = photo
            # Выполнение SQL-запроса для получения number_cells из базы данных по её идентификатору
            cursor.execute("SELECT number_cells FROM bingo_data WHERE id=?", (random_id,))
            data['number_cells'] = cursor.fetchone()
            # Закрытие соединения с базой данных
            conn.close()
        # Отправка фотографии
        await bot.send_photo(message.chat.id, photo=photo, reply_markup=bingo_selection_keyboard)
        # Установка состояния в 'waiting_for_action'
        await BingoStates.waiting_for_action.set()
    else:
        await message.answer('У вас нет созданных бинго. Создайте бинго с помощью команды /new_bingo')
        await state.finish()

async def process_my_bingo_action(message: types.Message, state: FSMContext):
    if message.text == '/stop' or message.text == 'Назад':
        await message.reply("Процесс остновлен", reply_markup=menu_keyboard)
        await state.finish()
    elif message.text == '❌ Следующее бинго':
        await send_bingo_command(message, state)
    elif message.text == '✅ Пройти бинго':
        # Get the selected bingo data
        async with state.proxy() as data:
            bingo_id = data.get('bingo_id')
        text_cells = get_bingo_data(bingo_id)

        if text_cells is None:
            await message.answer('Bingo data not found.')
            return

        # Store the bingo data in the state
        async with state.proxy() as data:
            data['text_cells'] = text_cells
            data['current_question'] = 0

        # Reset the global answers dictionary for each game of bingo
        global answers
        answers = {}

        # Set the state to 'passing'
        await PassBingo.passing.set()

        # Ask the next question
        question_text, current_question = await ask_next_question(message, state)

async def process_my_answer(message: types.Message, state: FSMContext):
    if message.text == '/stop' or message.text == 'Назад':
        await message.reply("Процесс остновлен", reply_markup=menu_keyboard)
        await state.finish()
    async with state.proxy() as data:
        if 'current_question' not in data:
                #await message.reply("Бинго не запущено. Начните новую игру.", reply_markup=menu_keyboard)
                await state.finish()
                return
    async with state.proxy() as data:
        current_question = data['current_question']  # Текущий вопрос
        text_cells = data['text_cells']  # Текстовые ячейки
        number_cells = data['number_cells'][0]  # Количество ячеек
        photo = data['photo']  # Фотография

    # Сохраняем фотографию во временный файл
    with open('temp_image.jpg', 'wb') as f:
        f.write(photo.getvalue())

    # Открываем временный файл и рисуем на нем
    img = Image.open('temp_image.jpg')

    # Преобразуем основное изображение в формат, поддерживающий прозрачность (RGBA), если это еще не сделано
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    draw = ImageDraw.Draw(img)

    if message.text == '✅':
        answers[current_question] = True
        text_cells[current_question] = '✅'

        if number_cells == 5:
            cell_size_x = 150 # Ширина
            cell_size_y = 150 # Высота
            board_offset_x = 150
            board_offset_y = 250
            cell_padding = 10 # Отступ от квадратов
        elif number_cells == 4:
            cell_size_x = 180
            cell_size_y = 180
            board_offset_x = 150
            board_offset_y = 250
            cell_padding = 10 # Отступ от квадратов
        elif number_cells == 3:
            cell_size_x = 250
            cell_size_y = 250
            board_offset_x = 150
            board_offset_y = 250
            cell_padding = 30 # Отступ от квадратов

        # Вычисляем позицию ячейки с отступом
        cell_x = current_question % number_cells
        cell_y = current_question // number_cells
        x1 = cell_x * (cell_size_x + cell_padding) + board_offset_x
        y1 = cell_y * (cell_size_y + cell_padding) + board_offset_y
        x2 = x1 + cell_size_x
        y2 = y1 + cell_size_y
        cell_position = (x1, y1, x2, y2)

        # Открываем фото, изменяем размеры и делаем его полупрозрачным
        photo = Image.open('photo\photo_putty.png')

        # Преобразуем фото в формат, поддерживающий прозрачность (RGBA), если это еще не сделано
        if photo.mode != 'RGBA':
            photo = photo.convert('RGBA')

        photo = photo.resize((cell_size_x, cell_size_y))

        # Создаем новый альфа-канал с нужной прозрачностью (128 соответствует 50% прозрачности)
        new_alpha = Image.new('L', photo.size, 128)

        # Заменяем альфа-канал фото на новый
        photo.putalpha(new_alpha)

        # Вставляем фото на основное изображение
        img.paste(photo, cell_position, mask=new_alpha)

    elif message.text == '❌':
        answers[current_question] = False
        text_cells[current_question] = '❌'

    else:
        await message.answer('Используй кнопки для выбора ответа')
        return

    # Сохраняем измененное изображение в объект BytesIO
    new_photo_bytes = BytesIO()
    img.save(new_photo_bytes, 'PNG')
    new_photo_bytes.seek(0)

    # Обновляем фотографию в состоянии
    async with state.proxy() as data:
        data['photo'] = new_photo_bytes

    if data['current_question'] == len(data['text_cells']) - 1:
        # Это был последний вопрос, вычисляем количество правильных ответов
        yes_count = sum(value for value in answers.values() if value == True)
        yes_count = yes_count * 100 // len(data['text_cells'])
        await bot.send_photo(message.chat.id, photo=data['photo'], caption=f'Твой результат <b>{yes_count}</b> % бинго поподаний!', reply_markup=menu_keyboard)

        await state.finish()
    else:
        # Увеличиваем счетчик текущего вопроса
        async with state.proxy() as data:
            data['current_question'] += 1

        # Задаем следующий вопрос
        question_text, current_question = await ask_next_question_my(message, state)

async def ask_next_question_my(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        current_question = data['current_question']
        text_cells = data['text_cells']

    # Ask the next question
    question_text = text_cells[current_question]

    # Send the photo
    await bot.send_photo(message.chat.id, photo=data['photo'], caption=f'Вопрос {current_question + 1}: <b>{question_text}</b>\nВыбери кнопкой ✅ или ❌', reply_markup=bingo_passing_keyboard)

    return question_text, current_question
