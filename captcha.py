# coding=utf-8
import random
import string
from PIL import Image, ImageDraw, ImageFont
import os
import numpy as np
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
import glob
import tensorflow as tf

font_path = 'Arial.ttf'
# 生成几位数的验证码
number = 4
# 生成验证码图片的高度和宽度
size = (150, 50)

# ###############   一些画验证码的函数   ###########################################
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

# ###############   分隔符   ###########################################

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

    # 删掉了保存label的txt，因为觉得没什么用

    # path_file_name = img_dir+'/hardness'+str(hardness)+'.txt'
    # if not os.path.exists(path_file_name):
    #     with open(path_file_name, "a") as f:
    #         print(f)
    # with open(path_file_name, "a") as f:
    #     f.write(text+'\n')
    return text


# on_hot编码

def to_onhot(text):
    #自定义字母顺序
    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    # define a mapping of chars to integers

    char_to_int = dict((c, i) for i, c in enumerate(alphabet))

    labels=[]
    # 遍历每一个验证码
    for onetext in text:
        print(onetext)
        # 将验证码的每一个字母变成对应的数字
        integer_encoded = [char_to_int[char] for char in onetext]
        print(integer_encoded)
        # one hot encode
        onehot_encoded = list()
        for value in integer_encoded:
            letter = [0 for _ in range(len(alphabet))]
            letter[value] = 1
            onehot_encoded.append(letter)
        labels.append(onehot_encoded)

    return labels


# 生成.npy文件
def gene_npy(hardness,set,labels):
    i=0
    # 判断保存在哪个集合
    if set == 1:
        img_dir = build_file_path('train/hardness'+str(hardness))
    if set == 2:
        img_dir = build_file_path('val/hardness'+str(hardness))
    # 获取所有图片的存储路径
    imgs = glob.glob(img_dir+'/hardness'+str(hardness)+'_*.png')
    # 初始化图片的array
    imgdatas = np.ndarray((len(imgs), 50, 150, 3), dtype=np.uint8)
    # 读取每一张图片
    for imgname in imgs:
        img = load_img(imgname)
        img = img_to_array(img)
        imgdatas[i] = img
        i += 1
    # 将label转为on_hot编码
    label_onhot=to_onhot(labels)

    # 生成npy文件
    np.save(img_dir + '/imgs.npy', imgdatas)
    print('loading done')
    np.save(img_dir + '/labels.npy', label_onhot)

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
        labels = []
        for j_train in range(cnt_train):
            label=gene_code(i,j_train,1)
            labels.append(label)

        print("generate train done.")
        gene_npy(i, 1, labels)
        labels = []
        for j_val in range(cnt_val):
            label=gene_code(i, j_val, 2)
            labels.append(label)
        gene_npy(i, 2, labels)
        print("generate validation done.")


