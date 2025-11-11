#!/usr/bin/env python3
"""测试优化后的代码"""

import numpy as np
from PIL import Image
import sys

# 创建测试图像
def create_test_image():
    # 创建一个包含6种E6颜色的测试图像
    width, height = 600, 400
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 分成6个区域，每个区域填充一种E6颜色
    colors = [
        [0, 0, 0],       # 黑色
        [255, 255, 255], # 白色
        [255, 255, 0],   # 黄色
        [255, 0, 0],     # 红色
        [0, 0, 255],     # 蓝色
        [0, 255, 0]      # 绿色
    ]
    
    block_width = width // 3
    block_height = height // 2
    
    for i, color in enumerate(colors):
        row = i // 3
        col = i % 3
        y1 = row * block_height
        y2 = (row + 1) * block_height
        x1 = col * block_width
        x2 = (col + 1) * block_width
        img[y1:y2, x1:x2] = color
    
    # 保存测试图像
    Image.fromarray(img).save('test_input.jpg')
    print('已创建测试图像: test_input.jpg')

if __name__ == '__main__':
    create_test_image()
    
    # 运行转换
    print('\n测试默认设置（photo预设，floyd抖动）:')
    import subprocess
    result = subprocess.run([sys.executable, '-m', 'convnew.main', 'test_input.jpg'], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print('错误:', result.stderr)
    
    print('\n测试无抖动模式:')
    result = subprocess.run([sys.executable, '-m', 'convnew.main', 'test_input.jpg', 
                           '--method', 'none', '--preset', 'logo'], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print('错误:', result.stderr)