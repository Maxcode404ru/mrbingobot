from PIL import Image, ImageDraw, ImageFont

# задаем шрифт и цвет текста
font = ImageFont.truetype('Caveat-Bold.ttf', 40)
text_color = (0, 0, 0)

# создаем изображение 1000x1000 пикселей
background = Image.new('RGB', (600, 800), color=(255,255,255))

draw = ImageDraw.Draw(background)

# открываем изображение таблицы и изменяем его размер
im_table = Image.open("table.png")
im_table = im_table.resize((500, 500), Image.BILINEAR)

# вставляем таблицу на фон
background.paste(im_table, (50, 250))
draw.text((180, 100), 'Бинго от Bibingo', font=font, fill=text_color)

# сохраняем изображение
background.save('photo.png')
