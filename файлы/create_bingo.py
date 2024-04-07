from PIL import Image, ImageDraw, ImageFont
# для преобразования в байтовые обьекты
import pickle
import re
import time


def creature_new_bingo(data, background_theme_photo, textFont):
    start_time = time.time()  # запоминаем текущее время перед вызовом функции

    number_cells = data['number_cells']
    print(number_cells)
    background_theme = data['background_theme']
    color_palette = data['color_palette']
    #two_colors = data['two_colors']

    name_bingo = data['name_bingo']
    font = data['font']
    text_cells = data['text_cells']

    text_color_name = 'black'
    text_color_info = 'grey'
    text_color = 'black'

    cell_size_1 = 0
    cell_size_2 = 0
    board_offset_x = 0
    board_offset_y = 0
    text_size = 0
    if number_cells == 5:
        cell_size_1 = 160
        cell_size_2 = 150
        board_offset_x = 150
        board_offset_y = 250
        text_size = 34
    elif number_cells == 4:
        cell_size_1 = 200
        cell_size_2 = 180
        board_offset_x = 150
        board_offset_y = 250
        text_size = 40

    elif number_cells == 3:
        cell_size_1 = 280
        cell_size_2 = 250
        board_offset_x = 150
        board_offset_y = 250
        text_size = 38

    else:
        print(number_cells)
        print("ERROR")




    # создаем изображение 3х3 4х4 5x5
    size = number_cells

    if textFont == '1':
    # задаем шрифт и цвет текста
        font_name = ImageFont.truetype('fonts/Another-Danger.ttf', 50)
        font_info = ImageFont.truetype('fonts/Another-Danger.ttf', 40)
        font_text = ImageFont.truetype('fonts/Another-Danger.ttf', text_size)
    elif textFont == '2':
        # задаем шрифт и цвет текста
        font_name = ImageFont.truetype('fonts/Bad Comic.ttf', 50)
        font_info = ImageFont.truetype('fonts/Bad Comic.ttf', 42)
        font_text = ImageFont.truetype('fonts/Bad Comic.ttf', text_size-10)
    if textFont == '3':
    # задаем шрифт и цвет текста
        font_name = ImageFont.truetype('fonts/Caveat-Bold.ttf', 50)
        font_info = ImageFont.truetype('fonts/Caveat-Bold.ttf', 44)
        font_text = ImageFont.truetype('fonts/Caveat-Bold.ttf', text_size)
    elif textFont == '4':
        # задаем шрифт и цвет текста
        font_name = ImageFont.truetype('fonts/Sweet Mavka Script.ttf', 50)
        font_info = ImageFont.truetype('fonts/Sweet Mavka Script.ttf', 40)
        font_text = ImageFont.truetype('fonts/Sweet Mavka Script.ttf', text_size-10)
    elif textFont == '5':
        # задаем шрифт и цвет текста
        font_name = ImageFont.truetype('fonts\Colus-Regular.otf', 54)
        font_info = ImageFont.truetype('fonts\Colus-Regular.otf', 38)
        font_text = ImageFont.truetype('fonts\Colus-Regular.otf', text_size-13)

    if background_theme == 'Цвет':
        # Если data - строка, выполняем одно действие
        print('String:', background_theme)
        background_theme_color = data['background_theme_color']
        img = Image.new('RGBA', (1080,1080), color=(background_theme_color))
    else:
        # Если data - не строка, проверяем, является ли data объектом Image
        if background_theme == 'Фото':


                img = Image.new('RGBA', (1080,1080), color=(216,216,216))
            # Если data - объект Image, выполняем другое действие
             # Открываем картинку, которую хотим наложить на фон
                img2 = Image.open('photo\\background.png')

            # Изменяем размер картинки
                new_size = (1080, 1080)
                img2 = img2.resize(new_size)

            # Определяем позицию, куда будем накладывать картинку
                position = (0, 0)

            # Накладываем картинку на фон
                img.paste(img2, position)
        else:
            # Если data - не строка и не объект Image, выводим сообщение об ошибке
            print('Error: unexpected data type')





    # #faf3dd / #ffa69e / #aed9e0
    # #e6e6fa / #fcfdaf / #dec0f1
    # #dcc0ed / #c0eddc / #eddcc0
    # #e6e6fa / #fcfdaf / #dec0f1




    # задаем цвета квадратов
    if color_palette == '2 цвета':
        two_colors = pickle.loads(data['two_colors'])
        colors_massiv = two_colors
        print(colors_massiv)
        colors = [colors_massiv[0], colors_massiv[1]]
    elif color_palette == '1 цвет':
        color_selection = data['color_selection']
        colors = [(color_selection), (255,255,255)]
    else:
        print('ERROR COLOR IN create_bingo.py')



    # создаем объект ImageDraw для рисования на изображении
    draw = ImageDraw.Draw(img)

    # задаем радиус скругления квадратов
    radius = 10

    # задаем массив текстов для каждого квадрата
    texts =  split_string_into_arrays(text_cells, number_cells, number_cells)

    t = [ #=================================================================================================!!!
        ["Пирог с \nяблоками", 'Пюрешка', "Эклер", 'Кола', 'Пепси'],
        ["Борщ", "Пельмени", "Блины", "Шашлык", "Оливье"],
        ["Шаума","Ржаной хлеб" , "Жаренная\n картошка", "Кофе", "Пирожки"],
        ['Чай', "Голубцы", 'Чиабатта', "Сушки", "Наполеон"],
        ['Птичье\nмолоко', "Бородинский\n    хлеб", 'Спрайт', "Чизкейк", 'Чебуреки']
    ]
    print(texts)
    # рисуем квадраты в шахматном порядке
    for i in range(size):
        for j in range(size):

            # определяем цвет квадрата
            color = colors[(i + j) % 2]

            # определяем координаты квадрата
            x1 = i * cell_size_1 + board_offset_x # горизантальное смещение квадрата
            y1 = j * cell_size_1 + board_offset_y # вертикальное смещение квадрата
            x2 = x1 + cell_size_2 # ширина квадртата
            y2 = y1 + cell_size_2 # высота квадртата

            # рисуем тень
            shadow_color = 'black'
            shadow_offset = 3
            draw.rounded_rectangle([x1 + shadow_offset, y1 + shadow_offset, x2 + shadow_offset, y2 + shadow_offset], radius=radius, fill=shadow_color)

            # рисуем квадрат
            draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=color)

            # добавляем текст внутри квадрата
            text_sub= re.sub(' ', '\n', texts[i][j]) # добавляет переход на новую строку если есть пробел
            text_w, text_h = draw.textsize(text_sub, font=font_text)
            draw.text(((x1 + x2) / 2 - text_w / 2, (y1 + y2) / 2 - text_h / 2), text_sub, font=font_text, fill=colors[(i + j + 1) % 2])

    # добавляем текст загаловка
    draw.text((410, 100), name_bingo, font=font_info, fill=text_color_name)
    draw.text((340, 150), 'Создано tg: @BibingoBot ', font=font_info, fill=text_color_info)

    # сохраняем изображение
    img.save('photo\checkerboard.png')
    end_time = time.time()  # запоминаем текущее время после вызова функции

    elapsed_time = end_time - start_time  # вычисляем время выполнения функции

    print(f'Бинго собралось за {elapsed_time:.6f} секунд')


def split_string_into_arrays(input_data, num_arrays, words_per_array):
    if isinstance(input_data, list):
        input_string = ', '.join(input_data)
    else:
        input_string = input_data

    words = input_string.split(', ')
    result = []
    start = 0
    for _ in range(num_arrays):
        end = start + words_per_array
        result.append(words[start:end])
        start = end
    return result
