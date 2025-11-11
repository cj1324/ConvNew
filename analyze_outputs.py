#!/usr/bin/env python3
"""Analyze and compare output files from both converters"""

import numpy as np
from PIL import Image
import os

# E6标准颜色
E6_COLORS = np.array([
    [0, 0, 0],        # 黑色
    [255, 255, 255],  # 白色  
    [255, 243, 56],   # 黄色
    [191, 0, 0],      # 红色
    [100, 64, 255],   # 蓝色
    [67, 138, 28]     # 绿色
], dtype=np.uint8)

# Backup convert.py palette colors (from line 83)
BACKUP_COLORS = np.array([
    [0, 0, 0],        # 黑色
    [255, 255, 255],  # 白色
    [255, 255, 0],    # 黄色 (注意：这里是纯黄色，不是E6黄色)
    [255, 0, 0],      # 红色 (注意：这里是纯红色，不是E6红色)
    [0, 0, 0],        # 又是黑色
    [0, 0, 255],      # 蓝色 (注意：这里是纯蓝色，不是E6蓝色)
    [0, 255, 0],      # 绿色 (注意：这里是纯绿色，不是E6绿色)
], dtype=np.uint8)

def analyze_image(filename, label):
    """分析图像的颜色分布"""
    if not os.path.exists(filename):
        print(f'{label}: 文件不存在 - {filename}')
        return None
    
    img = Image.open(filename)
    print(f'\n{label}: {filename}')
    print(f'  模式: {img.mode}, 尺寸: {img.size}')
    
    # 转换为RGB分析
    img_rgb = img.convert('RGB')
    img_array = np.array(img_rgb)
    unique_colors = np.unique(img_array.reshape(-1, 3), axis=0)
    
    print(f'  唯一颜色数: {len(unique_colors)}')
    
    # 统计每种颜色的像素数
    color_counts = {}
    flat_img = img_array.reshape(-1, 3)
    for color in unique_colors:
        count = np.sum(np.all(flat_img == color, axis=1))
        color_counts[tuple(color)] = count
    
    # 按数量排序显示
    sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
    
    print('  颜色分布:')
    color_names = ['黑色', '白色', '黄色', '红色', '蓝色', '绿色']
    for color_tuple, count in sorted_colors[:10]:
        color = np.array(color_tuple)
        percentage = count * 100 / (img_array.shape[0] * img_array.shape[1])
        print(f'    RGB{color_tuple}: {count:6d} pixels ({percentage:5.2f}%)', end='')
        
        # 检查是否是E6颜色
        for i, e6_color in enumerate(E6_COLORS):
            if np.array_equal(color, e6_color):
                print(f' -> E6 {color_names[i]}', end='')
                break
        
        # 检查是否是备份转换器的颜色
        for i, backup_color in enumerate(BACKUP_COLORS[:7]):
            if np.array_equal(color, backup_color):
                backup_names = ['黑', '白', '纯黄', '纯红', '黑2', '纯蓝', '纯绿']
                if i < len(backup_names):
                    print(f' -> Backup {backup_names[i]}', end='')
                break
        print()
    
    return img_array

print('=' * 70)
print('E6色彩转换器输出对比分析')
print('=' * 70)

# 分析原始测试图像
original = analyze_image('test_colors.jpg', '原始图像')

# 分析新转换器输出
new_output = analyze_image('test_colors_e6.bmp', '新转换器输出')

# 分析备份转换器输出  
backup_output = analyze_image('test_colors_scale_output.bmp', '备份转换器输出')

print('\n' + '=' * 70)
print('问题分析:')
print('=' * 70)

print('\n备份转换器使用的调色板颜色 (来自backup/convert.py第83行):')
print('  (0,0,0,  255,255,255,  255,255,0,  255,0,0,  0,0,0,  0,0,255,  0,255,0)')
print('  黑色     白色         纯黄色      纯红色    黑色     纯蓝色    纯绿色')

print('\nE6标准颜色:')
for i, (name, color) in enumerate(zip(['黑色', '白色', '黄色', '红色', '蓝色', '绿色'], E6_COLORS)):
    print(f'  {name}: RGB{tuple(color)}')

print('\n关键差异:')
print('1. 备份转换器使用的是纯色RGB值，不是E6标准色')
print('2. 备份转换器的调色板中有重复的黑色')
print('3. 新转换器正确使用了E6标准颜色')