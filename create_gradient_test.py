#!/usr/bin/env python3
"""创建渐变测试图像"""

from PIL import Image, ImageDraw
import numpy as np

# 创建渐变测试图像
img = Image.new('RGB', (800, 480), (255, 255, 255))
draw = ImageDraw.Draw(img)

# 创建不同的颜色渐变区域
width = 800
height = 480
section_height = height // 6

# 红色渐变
for y in range(section_height):
    intensity = int(255 * y / section_height)
    draw.rectangle([(0, y), (width, y+1)], fill=(intensity, 0, 0))

# 绿色渐变
for y in range(section_height):
    intensity = int(255 * y / section_height)
    draw.rectangle([(0, section_height + y), (width, section_height + y+1)], 
                   fill=(0, intensity, 0))

# 蓝色渐变
for y in range(section_height):
    intensity = int(255 * y / section_height)
    draw.rectangle([(0, 2*section_height + y), (width, 2*section_height + y+1)], 
                   fill=(0, 0, intensity))

# 黄色渐变
for y in range(section_height):
    intensity = int(255 * y / section_height)
    draw.rectangle([(0, 3*section_height + y), (width, 3*section_height + y+1)], 
                   fill=(intensity, intensity, 0))

# 灰度渐变
for y in range(section_height):
    intensity = int(255 * y / section_height)
    draw.rectangle([(0, 4*section_height + y), (width, 4*section_height + y+1)], 
                   fill=(intensity, intensity, intensity))

# 彩虹渐变
for x in range(width):
    hue = int(360 * x / width)
    # 简单的HSV到RGB转换
    c = 1.0
    h_i = hue // 60
    x_val = c * (1 - abs((hue / 60) % 2 - 1))
    
    if h_i == 0:
        r, g, b = c, x_val, 0
    elif h_i == 1:
        r, g, b = x_val, c, 0
    elif h_i == 2:
        r, g, b = 0, c, x_val
    elif h_i == 3:
        r, g, b = 0, x_val, c
    elif h_i == 4:
        r, g, b = x_val, 0, c
    else:
        r, g, b = c, 0, x_val
    
    rgb = (int(r * 255), int(g * 255), int(b * 255))
    draw.rectangle([(x, 5*section_height), (x+1, height)], fill=rgb)

img.save('gradient_test.png')
print('创建渐变测试图像: gradient_test.png')