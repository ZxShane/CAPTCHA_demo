# coding=utf-8
import random
import string
import sys
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

font_path = 'Arial.ttf'
# 生成几位数的验证码
number = 4
# 生成验证码图片的高度和宽度
size = (150, 50)

def getRandomColor1():
    r = random.randint(32, 127)
    g = random.randint(32, 127)
    b = random.randint(32, 127)
    return (r, g, b)

def getRandomColor2():
    r = random.randint(64, 255)
    g = random.randint(64, 255)
    b = random.randint(64, 255)
    return (r, g, b)

# 用来随机生成一个字符串
def gene_text():
    source = list(string.ascii_uppercase)
    for index in range(0, 10):
        source.append(str(index))
    return ''.join(random.sample(source, number))  # number是生成验证码的位数


# 用来绘制干扰线
def gene_line(draw, width, height,line_number):
    for line in range(line_number):
        begin = (random.randint(0, width), random.randint(0, height))
        end = (random.randint(0, width), random.randint(0, height))
        linecolor = (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))
        draw.line([begin, end], fill=getRandomColor2())

# 用来绘制干扰点
def drawPoint(draw,width,height,point_number):
    for i in range(point_number):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x,y), fill=getRandomColor2())

# 用来绘制干扰圆弧
def drawArc(draw,width,height,arc_number):
    for i in range(arc_number):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.arc((x, y, x + 8, y + 8), 0, 90, fill=getRandomColor2())

# 添加文件路径
def build_file_path(x):
    if not os.path.isdir('./imgs'):
        os.mkdir('./imgs')
    return os.path.join('./imgs', x)


# 生成验证码
def gene_code(hardness,j,set):
    # bgcolor = (random.randint(64, 255), random.randint(64, 255), random.randint(64, 255))
    # fontcolor = (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))
    if hardness == 0:
        draw_line = False
        draw_circle = False
        rotate=False
        bgcolor=(255,255,255)
    if hardness == 1:
        draw_line = True
        draw_circle = False
        rotate = True
        point_number = random.randint(5, 10)
        line_number = random.randint(3, 5)
        bgcolor = (232,232,232)
    if hardness == 2:
        draw_line = True
        draw_circle = True
        rotate = True
        point_number = random.randint(10, 20)
        arc_number = random.randint(5,10)
        line_number = random.randint(10,15)
        bgcolor = (136, 136, 136)

    width, height = size  # 宽和高
    image = Image.new('RGBA', (width, height), bgcolor)  # 创建图片
    font = ImageFont.truetype(font_path, 25)  # 验证码的字体
    draw = ImageDraw.Draw(image)  # 创建画笔
    text = gene_text()  # 生成字符串
    font_width, font_height = font.getsize(text)
    draw.text(((width - font_width) / number, (height - font_height) / number), text,
              font=font, fill=getRandomColor1())  # 填充字符串

    if draw_line:
        gene_line(draw, width, height,line_number)
        drawPoint(draw,width,height,point_number)
    if draw_circle:
        drawArc(draw, width, height, arc_number)

    if rotate:
        image = image.rotate(random.randint(-10, 20))
        draw = ImageDraw.Draw(image)  # 创建画笔

        for x in range(width):
            for y in range(height):
                c = image.getpixel((x, y))
                if c == (0, 0, 0, 0):
                    draw.point([x, y], fill=bgcolor)
    if set == 1:
        img_dir = build_file_path('train/hardness'+str(hardness))
    if set == 2:
        img_dir = build_file_path('val/hardness'+str(hardness))
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    image.save(img_dir+'/hardness'+str(hardness)+'_'+str(j+1)+'.png')  # 保存验证码图片
    path_file_name = img_dir+'/hardness'+str(hardness)+'.txt'
    if not os.path.exists(path_file_name):
        with open(path_file_name, "a") as f:
            print(f)
    with open(path_file_name, "a") as f:
        f.write(text+'\n')


if __name__ == "__main__":
    cnt_train = int(input("请输入需要训练集中生成的验证码数量:"))
    cnt_val = int(input("请输入需要交叉验证集中生成的验证码数量:"))
    for i in range(3):
        if i == 0:
            print("generating easy...")
        if i == 1:
            print("generating middle...")
        if i == 2:
            print("generating hard...")
        for j_train in range(cnt_train):
            gene_code(i,j_train,1)
        print("generate train done.")
        for j_val in range(cnt_val):
            gene_code(i, j_val,2)
        print("generate validation done.")


