#!/usr/bin/env python3
"""
测试脚本：验证固件兼容性改进
"""

import os
import sys
import numpy as np
from PIL import Image

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from convnew.main import test_firmware_compatibility, E6_COLORS

def create_test_image():
    """创建一个测试图像"""
    # 创建6色测试图像
    img = Image.new('RGB', (600, 400), (255, 255, 255))
    pixels = img.load()
    
    # 绘制6个颜色块
    colors = [
        (0, 0, 0),       # 黑色
        (255, 255, 255), # 白色
        (255, 255, 0),   # 黄色
        (255, 0, 0),     # 红色
        (0, 0, 255),     # 蓝色
        (0, 255, 0)      # 绿色
    ]
    
    for i, color in enumerate(colors):
        x_start = (i % 3) * 200
        y_start = (i // 3) * 200
        for x in range(x_start, x_start + 200):
            for y in range(y_start, y_start + 200):
                if x < 600 and y < 400:
                    pixels[x, y] = color
    
    # 添加一些渐变区域（用于测试量化）
    for x in range(100):
        for y in range(50):
            gray = int(x * 255 / 100)
            pixels[x, y + 350] = (gray, gray, gray)
    
    return img

def test_conversion():
    """测试转换流程"""
    print("=" * 60)
    print("固件兼容性测试")
    print("=" * 60)
    
    # 创建测试图像
    print("\n1. 创建测试图像...")
    test_img = create_test_image()
    test_img.save('test_firmware_input.png')
    print("   已保存: test_firmware_input.png")
    
    # 运行转换（不同模式）
    print("\n2. 测试不同转换模式...")
    
    modes = [
        ('--method floyd', 'Floyd-Steinberg抖动'),
        ('--method ordered', '有序抖动'),
        ('--method none', '无抖动'),
        ('--method floyd --strict', 'Floyd-Steinberg + 严格模式'),
    ]
    
    for mode_args, mode_desc in modes:
        print(f"\n   测试 {mode_desc}:")
        cmd = f"python -m convnew.main test_firmware_input.png {mode_args}"
        print(f"   命令: {cmd}")
        os.system(cmd)
        
        # 测试输出文件
        output_file = 'test_firmware_input_e6.bmp'
        if os.path.exists(output_file):
            print(f"\n   验证输出文件兼容性:")
            is_compatible, bad_pixels = test_firmware_compatibility(output_file)
            
            if not is_compatible and len(bad_pixels) > 0:
                print(f"   发现{len(bad_pixels)}个不兼容像素")
                # 分析不兼容像素
                unique_bad_colors = set()
                for x, y, r, g, b in bad_pixels[:100]:  # 最多分析100个
                    unique_bad_colors.add((r, g, b))
                print(f"   不兼容的颜色值: {unique_bad_colors}")
            
            # 重命名保存结果
            new_name = f'test_firmware_{mode_args.replace(" ", "_").replace("--", "")}_e6.bmp'
            os.rename(output_file, new_name)
            print(f"   结果保存为: {new_name}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

def analyze_existing_files():
    """分析现有的BMP文件"""
    print("\n3. 分析现有BMP文件...")
    
    bmp_files = [f for f in os.listdir('.') if f.endswith('_e6.bmp')]
    
    if bmp_files:
        print(f"   找到{len(bmp_files)}个BMP文件")
        for bmp_file in bmp_files:
            print(f"\n   分析: {bmp_file}")
            is_compatible, bad_pixels = test_firmware_compatibility(bmp_file)
            
            # 统计颜色分布
            img = Image.open(bmp_file)
            pixels = np.array(img)
            unique_colors = {}
            
            for color_idx, e6_color in enumerate(E6_COLORS):
                count = np.sum(np.all(pixels == e6_color, axis=2))
                if count > 0:
                    color_names = ['黑色', '白色', '黄色', '红色', '蓝色', '绿色']
                    unique_colors[color_names[color_idx]] = count
            
            total_pixels = pixels.shape[0] * pixels.shape[1]
            print(f"   颜色分布:")
            for color_name, count in unique_colors.items():
                percentage = (count / total_pixels) * 100
                print(f"     {color_name}: {count:6d} 像素 ({percentage:5.1f}%)")
    else:
        print("   未找到BMP文件")

if __name__ == "__main__":
    test_conversion()
    analyze_existing_files()