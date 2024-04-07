import sqlite3
def get_bingo_data_by_id(id):
    conn = sqlite3.connect('bingo_database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name_bingo, name_user, approved_bingo, bingo_photo FROM bingo_data WHERE id = ?", (id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return {'name_bingo': result[0], 'name_user': result[1], 'approved_bingo': result[2], 'bingo_photo': result[3]}
    else:
        return None


def update_bingo_data_by_id(bingo_id, approved_bingo): # bingo_id = id
    conn = sqlite3.connect('bingo_database.db')  # Подключение к базе данных SQLite
    cursor = conn.cursor()

    # Выполнение SQL-запроса для обновления состояния в таблице bingo_data
    cursor.execute("UPDATE bingo_data SET approved_bingo = ? WHERE id = ?", (approved_bingo, bingo_id))

    conn.commit()  # Применение изменений
    conn.close()  # Закрытие соединения с базой данных


# ФУНКЦИЯ преобразующая массив текста в строку и ибирающая лишние символы
def format_text_array(text_array):
    formatted_arr = [item.strip("[],'") for item in text_array]
    return '\n'.join(formatted_arr)
# ФУНКЦИЯ проверки является пользователь админом
def is_user_admin(user_name):
    conn = sqlite3.connect('bingo_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM admin_data WHERE admin_id=?', (user_name,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return True
    else:
        return False

# Функция создания таблицы с результатами бинго
def setup_database_result_bingo():
    conn = sqlite3.connect('bingo_database.db')
    cursor = conn.cursor()

    # Create the bingo_results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bingo_results (
            name_user TEXT,
            id_bingo INTEGER,
            number_cells INTEGER,
            text_cells TEXT,
            selected_cells TEXT
        );
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


# ФУНКЦИИ ДЛЯ ПРОХОЖДЕНИЯ БИНГО
def get_bingo_data(bingo_id):
    conn = sqlite3.connect('bingo_database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT text_cells FROM bingo_data WHERE id=?", (bingo_id,))
    result = cursor.fetchone()

    conn.close()

    if result is None:
        return None

    text_cells = result[0]
    return text_cells.split(',')
