from PIL import Image, ImageDraw, ImageFont


def text2png(text,
             fullpath,
             color='#000',
             bgcolor='#FFF',
             fontfullpath='font.ttf',
             fontsize=14,
             leftpadding=3,
             rightpadding=3,
             width=450):

    font = ImageFont.truetype(fontfullpath, fontsize)

    lines = []
    line = u''

    for word in text.split():
        if (font.getsize(line + ' ' + word)[0]
           <= (width - rightpadding - leftpadding)):
            line += ' ' + word
        else:
            lines.append(line[1:])
            line = u''
            line += ' ' + word

    if len(line) != 0:
        lines.append(line[1:])

    line_height = font.getsize(text)[1]
    img_height = line_height * (len(lines) + 1)

    img = Image.new('RGBA', (width, img_height), bgcolor)
    draw = ImageDraw.Draw(img)

    y = 0
    for line in lines:
        draw.text((leftpadding, y), line, color, font=font)
        y += line_height

    img.save(fullpath)
