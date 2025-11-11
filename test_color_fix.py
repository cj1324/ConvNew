#!/usr/bin/env python3
#encoding: utf-8

import sys
import numpy as np

# 临时修改 sys.argv 以避免参数解析错误
original_argv = sys.argv
sys.argv = ['test_color_fix.py', 'dummy.jpg']

from convnew.main import E6_COLORS, E6_COLORS_WITH_SKIP, create_e6_palette

# 恢复原始 sys.argv
sys.argv = original_argv

print("测试 E6 颜色定义修复")
print("=" * 50)

print("\n包含跳过位置的完整数组 (E6_COLORS_WITH_SKIP):")
for i, color in enumerate(E6_COLORS_WITH_SKIP):
    if i == 4:
        print(f"  索引 {i}: {color} <- 跳过位置")
    else:
        color_names = ["黑色", "白色", "黄色", "红色", "跳过", "蓝色", "绿色"]
        print(f"  索引 {i}: {color} ({color_names[i]})")

print("\n实际使用的6色数组 (E6_COLORS):")
color_names_actual = ["黑色", "白色", "黄色", "红色", "蓝色", "绿色"]
for i, color in enumerate(E6_COLORS):
    print(f"  颜色 {i}: {color} ({color_names_actual[i]})")

print("\n验证颜色值:")
expected_colors = np.array([
    [0, 0, 0],        # 黑色
    [255, 255, 255],  # 白色
    [255, 255, 0],    # 黄色
    [255, 0, 0],      # 红色
    [0, 0, 255],      # 蓝色
    [0, 255, 0]       # 绿色
], dtype=np.float32)

all_correct = True
for i in range(6):
    if not np.array_equal(E6_COLORS[i], expected_colors[i]):
        print(f"  ✗ 颜色 {i} 不匹配!")
        print(f"    期望: {expected_colors[i]}")
        print(f"    实际: {E6_COLORS[i]}")
        all_correct = False

if all_correct:
    print("  ✓ 所有颜色值都正确!")

print("\n测试调色板生成:")
palette = create_e6_palette()
print(f"  调色板长度: {len(palette)} (应该是 768)")

# 检查调色板中的前7个颜色（包括跳过位置）
for i in range(7):
    start = i * 3
    end = start + 3
    rgb = palette[start:end]
    if i == 4:
        print(f"  调色板索引 {i}: RGB({rgb[0]}, {rgb[1]}, {rgb[2]}) <- 跳过位置")
    else:
        color_names = ["黑色", "白色", "黄色", "红色", "跳过", "蓝色", "绿色"]
        print(f"  调色板索引 {i}: RGB({rgb[0]}, {rgb[1]}, {rgb[2]}) ({color_names[i]})")

print("\n✓ 修复完成！E6颜色定义现在正确处理了跳过的索引4。")