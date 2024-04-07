from PIL import Image, ImageDraw, ImageFont
import pickle
import re
import time


from PIL import Image, ImageDraw

def paint_bingo_cells(bingo_image_path, cell_count, bingo_data):
    # Открываем изображение бинго
    bingo_image = Image.open(bingo_image_path)
    # Определяем размеры изображения
    image_width, image_height = bingo_image.size

    # Определяем размеры одной ячейки
    cell_width = image_width // cell_count
    cell_height = image_height // cell_count

    # Создаем объект ImageDraw для рисования на изображении
    draw = ImageDraw.Draw(bingo_image)

    # Перебираем данные бинго и закрашиваем соответствующие ячейки
    for key in bingo_data:
        # Получаем координаты ячейки
        row = int(key[0]) - 1
        col = int(key[1]) - 1

        # Вычисляем координаты верхнего левого и нижнего правого углов ячейки
        left = col * cell_width
        top = row * cell_height
        right = left + cell_width
        bottom = top + cell_height

        # Закрашиваем ячейку
        draw.rectangle([left, top, right, bottom], fill='red')

    # Сохраняем изображение с закрашенными ячейками
    bingo_image.save('bingo_with_marked_cells.jpg')
