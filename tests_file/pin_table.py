from PIL import Image, ImageDraw, ImageFont

# создаем изображение 300x300 пикселей
img = Image.new('RGB', (500, 500), color=(255,255,255))

draw = ImageDraw.Draw(img)

# задаем цвет линий
line_color = (0, 0, 0)

# задаем шрифт
font = ImageFont.truetype('Caveat-Bold.ttf', 22)

# задаем цвет текста
text_color = (0, 0, 0)

# задаем массив с текстом
text_array = [
    ['Любишь ли ты \n читать книги?', 'Играешь ли ты \nна муз \nинструменте?', 'Любишь ли ты \n есть острое?'],
    ['Любишь ли ты \nсмотреть на \nзвезды?', 'Часто ли ты \nшутишь?', 'Ты смотришь \n Аниме?'],
    ['Ты часто \nделаешь \n фотографии?', 'Ты не всташь с \n первого \nбудильника?', 'TG:BibingoBot']
]

# рисуем горизонтальные линии
for i in range(1, 4):
    if i == 1:
        draw.line([(0, i), (500, i)], fill=line_color, width=5)
    y = i * 166
    print(i)
    draw.line([(0, y), (500, y)], fill=line_color, width=5)

# рисуем вертикальные линии
for i in range(1, 4):
    if i == 1:
        draw.line([(i, 0), (i, 500)], fill=line_color, width=5)
    x = i * 166
    draw.line([(x, 0), (x, 500)], fill=line_color, width=5)


# рисуем текст в клетках
for i in range(0,3, 1):
    for j in range(0, 3, 1):
        x = j * 166 + 15
        y = i * 170 + 30

        text = text_array[i][j]
        draw.text((x, y), text, font=font, fill=text_color)

# сохраняем изображение
img.save('table.png')