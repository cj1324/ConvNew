#encoding: utf-8

import sys
import os
import os.path
import glob
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np
import argparse
import warnings
warnings.filterwarnings('ignore')

# E Ink E6 标准6色定义 (包含一个跳过位置)
E6_COLORS_WITH_SKIP = np.array([
    [0, 0, 0],        # 黑色
    [255, 255, 255],  # 白色  
    [255, 255, 0],   # 黄色
    [255, 0, 0],      # 红色
    [0, 0, 0],        # 跳过定义 (占位)
    [0, 0, 255],      # 蓝色
    [0, 255, 0]       # 绿色
], dtype=np.float32)

# 实际使用的6色 (排除跳过的位置)
E6_COLORS = np.array([
    E6_COLORS_WITH_SKIP[0],  # 黑色
    E6_COLORS_WITH_SKIP[1],  # 白色
    E6_COLORS_WITH_SKIP[2],  # 黄色
    E6_COLORS_WITH_SKIP[3],  # 红色
    E6_COLORS_WITH_SKIP[5],  # 蓝色 (跳过索引4)
    E6_COLORS_WITH_SKIP[6]   # 绿色
], dtype=np.float32)

def create_e6_palette():
    """创建E6专用调色板 (处理跳过的颜色索引)"""
    palette = []
    # 使用包含跳过位置的完整数组来创建调色板
    for i, color in enumerate(E6_COLORS_WITH_SKIP.astype(np.uint8)):
        if i == 4:  # 跳过索引4
            # 为跳过的位置填充黑色（或任意颜色，因为不会被使用）
            palette.extend([0, 0, 0])
        else:
            palette.extend(color.tolist())
    while len(palette) < 768:
        palette.extend([0, 0, 0])
    return palette

def find_nearest_color(pixel, colors):
    """找到最近的颜色"""
    distances = np.sum((colors - pixel) ** 2, axis=1)
    nearest = colors[np.argmin(distances)]
    # 确保返回纯色值（0或255），固件要求严格匹配
    nearest = np.where(nearest > 127, 255, 0)
    return nearest

def floyd_steinberg_dither(img_array, colors):
    """Floyd-Steinberg抖动算法（稳定版）"""
    height, width = img_array.shape[:2]
    # 使用float64避免精度问题
    img_float = img_array.astype(np.float64).copy()
    
    for y in range(height):
        for x in range(width):
            old_pixel = img_float[y, x]
            # 限制范围
            old_pixel = np.clip(old_pixel, 0, 255)
            
            # 找到最近颜色
            new_pixel = find_nearest_color(old_pixel, colors.astype(np.float64))
            img_float[y, x] = new_pixel
            
            # 计算误差
            error = old_pixel - new_pixel
            
            # 分配误差（使用标准系数）
            if x + 1 < width:
                img_float[y, x + 1] += error * 7/16
                img_float[y, x + 1] = np.clip(img_float[y, x + 1], 0, 255)
            
            if y + 1 < height:
                if x > 0:
                    img_float[y + 1, x - 1] += error * 3/16
                    img_float[y + 1, x - 1] = np.clip(img_float[y + 1, x - 1], 0, 255)
                
                img_float[y + 1, x] += error * 5/16
                img_float[y + 1, x] = np.clip(img_float[y + 1, x], 0, 255)
                
                if x + 1 < width:
                    img_float[y + 1, x + 1] += error * 1/16
                    img_float[y + 1, x + 1] = np.clip(img_float[y + 1, x + 1], 0, 255)
    
    return np.clip(img_float, 0, 255).astype(np.uint8)

def ordered_dither(img_array, colors):
    """有序抖动（Bayer矩阵）"""
    height, width = img_array.shape[:2]
    
    # 4x4 Bayer矩阵
    bayer_matrix = np.array([
        [0, 8, 2, 10],
        [12, 4, 14, 6],
        [3, 11, 1, 9],
        [15, 7, 13, 5]
    ], dtype=np.float32) * 16
    
    # 扩展Bayer矩阵
    bayer_tiled = np.tile(bayer_matrix, 
                          (height // 4 + 1, width // 4 + 1))[:height, :width]
    
    # 添加抖动
    img_dithered = img_array.astype(np.float32) + \
                   np.stack([bayer_tiled] * 3, axis=-1) - 128
    img_dithered = np.clip(img_dithered, 0, 255)
    
    # 量化
    result = np.zeros_like(img_array, dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            result[y, x] = find_nearest_color(img_dithered[y, x], colors)
    
    return result

def simple_quantize(img_array, colors):
    """简单量化（无抖动）"""
    height, width = img_array.shape[:2]
    result = np.zeros_like(img_array, dtype=np.uint8)
    
    for y in range(height):
        for x in range(width):
            result[y, x] = find_nearest_color(img_array[y, x], colors)
    
    return result

def force_pure_colors(img_array):
    """强制输出为纯色值（0或255），确保固件兼容性"""
    result = img_array.copy()
    # 将所有通道值量化为0或255
    result = np.where(result < 128, 0, 255)
    return result.astype(np.uint8)

def validate_and_fix_e6_colors(img_array):
    """验证并修正所有像素为有效的E6颜色"""
    valid_colors = np.array([
        [0, 0, 0],       # 黑色
        [255, 255, 255], # 白色
        [255, 255, 0],   # 黄色
        [255, 0, 0],     # 红色
        [0, 0, 255],     # 蓝色
        [0, 255, 0]      # 绿色
    ], dtype=np.uint8)
    
    height, width = img_array.shape[:2]
    result = img_array.copy()
    
    for y in range(height):
        for x in range(width):
            pixel = result[y, x]
            # 检查是否是有效的E6颜色
            is_valid = False
            for valid_color in valid_colors:
                if np.array_equal(pixel, valid_color):
                    is_valid = True
                    break
            
            if not is_valid:
                # 找最近的有效E6颜色
                result[y, x] = find_nearest_color(pixel, valid_colors.astype(np.float32))
    
    return result

def test_firmware_compatibility(bmp_path):
    """测试BMP文件是否与固件完全兼容"""
    try:
        img = Image.open(bmp_path)
        pixels = np.array(img)
        
        incompatible_pixels = []
        total_pixels = pixels.shape[0] * pixels.shape[1]
        
        for y in range(pixels.shape[0]):
            for x in range(pixels.shape[1]):
                r, g, b = pixels[y, x]
                # 模拟固件的精确匹配逻辑（参考GUI_BMPfile.c）
                if not ((r==0 and g==0 and b==0) or          # 黑色
                       (r==255 and g==255 and b==255) or      # 白色
                       (r==255 and g==255 and b==0) or        # 黄色
                       (r==255 and g==0 and b==0) or          # 红色
                       (r==0 and g==0 and b==255) or          # 蓝色
                       (r==0 and g==255 and b==0)):           # 绿色
                    incompatible_pixels.append((x, y, r, g, b))
        
        is_compatible = len(incompatible_pixels) == 0
        
        if is_compatible:
            print(f'✓ 固件兼容性测试通过: 所有{total_pixels}个像素都是有效的E6颜色')
        else:
            print(f'✗ 固件兼容性测试失败: 发现{len(incompatible_pixels)}个不兼容像素')
            if len(incompatible_pixels) <= 10:
                for x, y, r, g, b in incompatible_pixels[:10]:
                    print(f'  位置({x},{y}): RGB({r},{g},{b})')
        
        return is_compatible, incompatible_pixels
    except Exception as e:
        print(f'测试失败: {e}')
        return False, []

def preprocess_image(img, config):
    """预处理图像（使用PIL）"""
    # 确保是RGB模式
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # 1. 自动对比度
    if config.get('auto_balance', True):
        img = ImageOps.autocontrast(img, cutoff=2)
    
    # 2. 去噪
    if config.get('denoise', False):
        img = img.filter(ImageFilter.MedianFilter(size=3))
    
    # 3. 色彩增强
    color_enhance = config.get('color_enhance', 1.0)
    if color_enhance != 1.0:
        img = ImageEnhance.Color(img).enhance(color_enhance)
    
    # 4. 对比度
    contrast = config.get('contrast', 1.0)
    if contrast != 1.0:
        img = ImageEnhance.Contrast(img).enhance(contrast)
    
    # 5. 亮度
    brightness = config.get('brightness', 1.0)
    if brightness != 1.0:
        img = ImageEnhance.Brightness(img).enhance(brightness)
    
    # 6. 锐化
    sharpen = config.get('sharpen', 1.0)
    if sharpen > 1.0:
        img = ImageEnhance.Sharpness(img).enhance(sharpen)
    
    # 7. 边缘增强
    if config.get('edge_enhance', False):
        img = img.filter(ImageFilter.EDGE_ENHANCE)
    
    # 确保返回RGB
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    return img

def optimize_colors(img_array):
    """优化颜色以适应6色显示，增强固件兼容性"""
    result = img_array.copy().astype(np.float32)
    
    # 增强主色调
    for y in range(result.shape[0]):
        for x in range(result.shape[1]):
            r, g, b = result[y, x]
            
            # 增强纯色倾向
            max_val = max(r, g, b)
            min_val = min(r, g, b)
            
            if max_val - min_val > 80:  # 有明显主色
                # 增强主色，减弱其他色
                if r == max_val:
                    r = min(255, r * 1.2)  # 更强的增强
                    g *= 0.85
                    b *= 0.85
                elif g == max_val:
                    g = min(255, g * 1.2)
                    r *= 0.85
                    b *= 0.85
                elif b == max_val:
                    b = min(255, b * 1.2)
                    r *= 0.85
                    g *= 0.85
            
            # 特别优化黄色（固件期望R=255,G=255,B=0）
            if r > 200 and g > 200 and b < 50:  # 更严格的黄色检测
                # 强制为纯黄色
                r = 255
                g = 255
                b = 0
            # 优化接近纯色的像素
            elif r > 200 and g < 100 and b < 100:  # 偏红
                r = 255
                g = 0
                b = 0
            elif r < 100 and g > 200 and b < 100:  # 偏绿
                r = 0
                g = 255
                b = 0
            elif r < 100 and g < 100 and b > 200:  # 偏蓝
                r = 0
                g = 0
                b = 255
            
            result[y, x] = [r, g, b]
    
    return np.clip(result, 0, 255).astype(np.uint8)

def process_single_image(input_file, args, config):
    """处理单个图像文件"""
    if not os.path.isfile(input_file):
        print(f'警告：文件 {input_file} 不存在，跳过')
        return False
    
    print(f'\n处理图像: {input_file}')
    print(f'预设: {args.preset}, 抖动: {args.method}')
    
    try:
        # 打开图像并强制转换为RGB
        img = Image.open(input_file)
        # 重要：确保是RGB模式
        if img.mode != 'RGB':
            print(f'转换图像模式: {img.mode} -> RGB')
            img = img.convert('RGB')
        
        original_size = img.size
        
        # 确定目标尺寸
        if args.dir == 'landscape':
            target_w, target_h = 800, 480
        elif args.dir == 'portrait':
            target_w, target_h = 480, 800
        else:  # auto
            if img.width > img.height:
                target_w, target_h = 800, 480
            else:
                target_w, target_h = 480, 800
        
        print(f'原始尺寸: {original_size[0]}x{original_size[1]}')
        print(f'目标尺寸: {target_w}x{target_h}')
        
        # 调整尺寸
        if args.mode == 'fit':
            # 保持比例适应
            img.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
            # 创建白色背景
            new_img = Image.new('RGB', (target_w, target_h), (255, 255, 255))
            # 居中粘贴
            left = (target_w - img.width) // 2
            top = (target_h - img.height) // 2
            new_img.paste(img, (left, top))
            img = new_img
        elif args.mode == 'fill':
            # 填充整个区域（可能裁剪）
            img_ratio = img.width / img.height
            target_ratio = target_w / target_h
            
            if img_ratio > target_ratio:
                # 按高度缩放
                new_h = target_h
                new_w = int(target_h * img_ratio)
            else:
                # 按宽度缩放
                new_w = target_w
                new_h = int(target_w / img_ratio)
            
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            # 裁剪中心区域
            left = (new_w - target_w) // 2
            top = (new_h - target_h) // 2
            img = img.crop((left, top, left + target_w, top + target_h))
        else:  # stretch
            # 拉伸到目标尺寸
            img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        # 确保调整后仍是RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        print('应用预处理...')
        # 预处理
        img = preprocess_image(img, config)
        
        # 转换为numpy数组
        img_array = np.array(img, dtype=np.uint8)
        
        # 颜色优化
        if config.get('optimize_colors', True):
            print('优化颜色...')
            img_array = optimize_colors(img_array)
        
        # 应用量化
        print(f'应用{args.method}量化...')
        
        if args.method == 'floyd':
            quantized = floyd_steinberg_dither(img_array, E6_COLORS)
        elif args.method == 'ordered':
            quantized = ordered_dither(img_array, E6_COLORS)
        else:  # none
            quantized = simple_quantize(img_array, E6_COLORS)
        
        # 如果启用严格模式或者总是强制纯色化（推荐）
        if args.strict or True:  # 默认总是启用以确保固件兼容
            # 强制纯色化，确保固件兼容性
            quantized = force_pure_colors(quantized)
            
            # 验证E6颜色
            quantized = validate_and_fix_e6_colors(quantized)
            
            if args.strict:
                print('  已应用严格固件兼容模式')
        
        # 转换回PIL图像（确保RGB模式）
        result_img = Image.fromarray(quantized, mode='RGB')
        
        # 创建调色板图像
        pal_img = Image.new('P', (1, 1))
        pal_img.putpalette(create_e6_palette())
        
        # 量化到6色调色板
        final_img = result_img.convert('RGB').quantize(palette=pal_img).convert('RGB')
        
        # 保存BMP文件（24位格式，固件要求）
        output_file = os.path.splitext(input_file)[0] + f'_e6.bmp'
        final_img.save(output_file, 'BMP')  # PIL会自动使用24位BMP格式
        
        # 保存RGB预览
        preview_file = os.path.splitext(input_file)[0] + f'_preview.png'
        # 转回RGB保存预览
        preview_img = final_img.convert('RGB')
        preview_img.save(preview_file, 'PNG')
        
        print(f'✓ 转换完成: {output_file}')
        print(f'  预览文件: {preview_file}')
        print(f'  最终尺寸: {target_w}x{target_h}')
        
        # 自动运行固件兼容性测试
        print('\n运行固件兼容性测试...')
        test_firmware_compatibility(output_file)
        
        return True
        
    except Exception as e:
        print(f'✗ 处理 {input_file} 时出错: {str(e)}')
        return False

# 参数解析
parser = argparse.ArgumentParser(
    description='E Ink E6 六色墨水屏图像转换工具',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog='''
使用示例:
  python main.py image.jpg                       # 处理单个文件
  python main.py /path/to/directory              # 处理目录中所有图片
  python main.py image.jpg --preset art          # 艺术作品模式
  python main.py ./photos --method ordered       # 对目录使用有序抖动
  python main.py image.jpg --no-dither           # 无抖动
    '''
)

parser.add_argument('input_path', type=str, help='输入图像文件或目录路径')
parser.add_argument('--preset', choices=['photo', 'art', 'text', 'logo'], 
                   default='photo', help='预设模式')
parser.add_argument('--method', choices=['floyd', 'ordered', 'none'], 
                   default='floyd', help='抖动方法')
parser.add_argument('--dir', choices=['landscape', 'portrait', 'auto'], 
                   default='auto', help='显示方向')
parser.add_argument('--mode', choices=['fit', 'fill', 'stretch'], 
                   default='fit', help='缩放模式')
parser.add_argument('--no-dither', action='store_true', 
                   help='禁用抖动')
parser.add_argument('--enhance', type=float, default=None, 
                   help='色彩增强系数 (1.0-2.0)')
parser.add_argument('--contrast', type=float, default=None, 
                   help='对比度系数 (1.0-2.0)')
parser.add_argument('--brightness', type=float, default=None, 
                   help='亮度系数 (0.8-1.2)')
parser.add_argument('--strict', action='store_true',
                   help='严格固件兼容模式（强制纯色输出）')
parser.add_argument('--test-only', action='store_true',
                   help='仅测试现有BMP文件的固件兼容性')

args = parser.parse_args()

# 检查输入路径
if not os.path.exists(args.input_path):
    print(f'错误：路径 {args.input_path} 不存在')
    sys.exit(1)

# 如果是仅测试模式
if args.test_only:
    if args.input_path.lower().endswith('.bmp'):
        print(f'测试BMP文件的固件兼容性: {args.input_path}')
        is_compatible, _ = test_firmware_compatibility(args.input_path)
        sys.exit(0 if is_compatible else 1)
    else:
        print('错误：--test-only 参数需要一个BMP文件路径')
        sys.exit(1)

# 预设配置
presets = {
    'photo': {
        'color_enhance': 1.5,
        'contrast': 1.3,
        'brightness': 1.0,
        'sharpen': 1.2,
        'denoise': True,
        'auto_balance': True,
        'edge_enhance': False,
        'optimize_colors': True
    },
    'art': {
        'color_enhance': 1.8,
        'contrast': 1.5,
        'brightness': 1.0,
        'sharpen': 1.4,
        'denoise': False,
        'auto_balance': True,
        'edge_enhance': False,
        'optimize_colors': True
    },
    'text': {
        'color_enhance': 1.0,
        'contrast': 1.7,
        'brightness': 1.1,
        'sharpen': 1.6,
        'denoise': False,
        'auto_balance': True,
        'edge_enhance': True,
        'optimize_colors': False
    },
    'logo': {
        'color_enhance': 2.0,
        'contrast': 1.4,
        'brightness': 1.0,
        'sharpen': 1.3,
        'denoise': False,
        'auto_balance': False,
        'edge_enhance': False,
        'optimize_colors': True
    }
}

# 获取配置
config = presets[args.preset].copy()

# 应用命令行参数覆盖
if args.enhance is not None:
    config['color_enhance'] = args.enhance
if args.contrast is not None:
    config['contrast'] = args.contrast
if args.brightness is not None:
    config['brightness'] = args.brightness
if args.no_dither:
    args.method = 'none'

# 判断是文件还是目录
if os.path.isfile(args.input_path):
    # 处理单个文件
    success = process_single_image(args.input_path, args, config)
    if not success:
        sys.exit(1)
elif os.path.isdir(args.input_path):
    # 处理目录中的所有图片
    print(f'扫描目录: {args.input_path}')
    
    # 支持的图片格式
    patterns = ['*.jpg', '*.jpeg', '*.JPG', '*.JPEG', '*.png', '*.PNG', '*.bmp', '*.BMP']
    image_files = []
    
    for pattern in patterns:
        search_path = os.path.join(args.input_path, pattern)
        image_files.extend(glob.glob(search_path))
    
    # 去重并排序
    image_files = sorted(list(set(image_files)))
    
    if not image_files:
        print(f'错误：目录 {args.input_path} 中没有找到图片文件')
        sys.exit(1)
    
    print(f'找到 {len(image_files)} 个图片文件')
    print('-' * 60)
    
    success_count = 0
    failed_count = 0
    
    for i, image_file in enumerate(image_files, 1):
        print(f'\n[{i}/{len(image_files)}] ', end='')
        if process_single_image(image_file, args, config):
            success_count += 1
        else:
            failed_count += 1
    
    print('\n' + '=' * 60)
    print(f'处理完成！')
    print(f'成功: {success_count} 个文件')
    if failed_count > 0:
        print(f'失败: {failed_count} 个文件')
else:
    print(f'错误：{args.input_path} 既不是文件也不是目录')
    sys.exit(1)
