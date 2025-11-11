#!/usr/bin/env python3
"""测试E6颜色转换的脚本"""

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

def create_test_image():
    """创建包含所有E6颜色的测试图像"""
    # 创建一个600x400的图像，每种颜色占100x200的区域
    img = Image.new('RGB', (600, 400))
    pixels = img.load()
    
    # 绘制6个颜色块
    for i, color in enumerate(E6_COLORS):
        x_start = (i % 3) * 200
        y_start = (i // 3) * 200
        color_tuple = tuple(color.tolist())
        
        for x in range(x_start, x_start + 200):
            for y in range(y_start, y_start + 200):
                pixels[x, y] = color_tuple
    
    # 保存测试图像
    img.save('test_e6_input.png')
    print('创建测试图像: test_e6_input.png')
    return 'test_e6_input.png'

def analyze_bmp(filename):
    """分析BMP文件的颜色"""
    if not os.path.exists(filename):
        print(f'文件不存在: {filename}')
        return
    
    img = Image.open(filename)
    print(f'\n分析文件: {filename}')
    print(f'图像模式: {img.mode}')
    print(f'图像尺寸: {img.size}')
    
    # 获取调色板信息
    if img.mode == 'P':
        palette = img.getpalette()
        if palette:
            print('检测到索引色模式，调色板前6个颜色:')
            for i in range(6):
                r = palette[i*3]
                g = palette[i*3 + 1]
                b = palette[i*3 + 2]
                print(f'  颜色{i}: RGB({r}, {g}, {b})')
                
                # 检查是否匹配E6颜色
                for j, e6_color in enumerate(E6_COLORS):
                    if r == e6_color[0] and g == e6_color[1] and b == e6_color[2]:
                        color_names = ['黑色', '白色', '黄色', '红色', '蓝色', '绿色']
                        print(f'    -> 匹配E6颜色: {color_names[j]}')
                        break
    
    # 转换为RGB分析实际颜色
    img_rgb = img.convert('RGB')
    img_array = np.array(img_rgb)
    unique_colors = np.unique(img_array.reshape(-1, 3), axis=0)
    
    print(f'\n图像中的唯一颜色数: {len(unique_colors)}')
    print('实际颜色值:')
    
    color_names = ['黑色', '白色', '黄色', '红色', '蓝色', '绿色']
    for color in unique_colors[:10]:  # 最多显示10种颜色
        print(f'  RGB({color[0]}, {color[1]}, {color[2]})', end='')
        
        # 检查是否是E6颜色
        for i, e6_color in enumerate(E6_COLORS):
            if np.array_equal(color, e6_color):
                print(f' -> E6 {color_names[i]}', end='')
                break
        print()
    
    if len(unique_colors) > 10:
        print(f'  ... 还有 {len(unique_colors) - 10} 种颜色')
    
    # 验证是否只包含E6颜色
    all_e6 = True
    for color in unique_colors:
        is_e6 = False
        for e6_color in E6_COLORS:
            if np.array_equal(color, e6_color):
                is_e6 = True
                break
        if not is_e6:
            all_e6 = False
            break
    
    if all_e6:
        print('\n✓ 图像只包含E6标准颜色')
    else:
        print('\n✗ 警告：图像包含非E6颜色')

if __name__ == '__main__':
    print('E6颜色转换测试工具')
    print('=' * 60)
    
    # 创建测试图像
    test_file = create_test_image()
    
    # 运行转换
    print('\n运行转换...')
    import subprocess
    result = subprocess.run([
        'python', '-m', 'convnew.main', 
        test_file, 
        '--preset', 'logo',
        '--method', 'none'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print('转换成功')
        print(result.stdout)
    else:
        print('转换失败')
        print(result.stderr)
    
    # 分析输出文件
    output_bmp = 'test_e6_input_e6.bmp'
    if os.path.exists(output_bmp):
        analyze_bmp(output_bmp)
    
    # 分析预览文件
    preview_png = 'test_e6_input_preview.png'
    if os.path.exists(preview_png):
        print('\n' + '=' * 60)
        analyze_bmp(preview_png)