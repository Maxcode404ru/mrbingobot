from PIL import Image, ImageDraw, ImageFont

# Показываем возможные шрифты
def create_text_image(text):
    # Создаем изображение
    image = Image.new('RGBA', (640, 640), 'white')
    font_size = 40
    line_spacing = 20
    max_width = 640 - 150
    # Создаем объект ImageDraw
    draw = ImageDraw.Draw(image)

    # Список путей к файлам шрифтов
    fonts= [
        'fonts\Angeme.ttf',
        'fonts/Bad Comic.ttf',
        'fonts/Caveat-Bold.ttf',
        'fonts/Sweet Mavka Script.ttf',
        'fonts/Colus-Regular.otf',
    ]

    # Определяем начальную позицию текста
    x = 150
    y = 200
    i = 1
    # Печатаем текст в столбик, меняя шрифты
    for font in fonts:
        # Загружаем шрифт
        font = ImageFont.truetype(font, font_size)

        # Разбиваем текст на строки, которые помещаются в одну строку
        lines = []
        line = ''
        for word in text.split():
            if draw.textsize(line + ' ' + word, font=font)[0] <= max_width:
                line += ' ' + word
            else:
                lines.append(line)
                line = word
        lines.append(line)

        # Определяем отступы и центрируем текст
        max_line_width = max([draw.textsize(line, font=font)[0] for line in lines])
        x = (image.width - max_line_width) / 2

        # Рисуем строки на изображении
        for j, line in enumerate(lines):
            draw.text((x, y + j * (font_size + line_spacing)), f"{line}", font=font, fill='white', stroke_width=5, stroke_fill='black')

        # Увеличиваем позицию y для следующей строки
        y += len(lines) * (font_size + line_spacing)

        # Увеличиваем счетчик строк
        i += len(lines)

    # Сохраняем изображение
    image.save('photo\\text_fonts_exemple.png')

create_text_image('денежное бинго')
