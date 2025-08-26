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

# E Ink E6 标准6色定义
E6_COLORS = np.array([
    [0, 0, 0],        # 黑色
    [255, 255, 255],  # 白色  
    [255, 255, 0],    # 黄色
    [255, 0, 0],      # 红色
    [0, 0, 255],      # 蓝色
    [0, 255, 0]       # 绿色
], dtype=np.float32)

# 为了兼容性保留带跳过的版本
E6_COLORS_WITH_SKIP = np.array([
    E6_COLORS[0],     # 黑色
    E6_COLORS[1],     # 白色
    E6_COLORS[2],     # 黄色
    E6_COLORS[3],     # 红色
    [0, 0, 0],        # 跳过定义 (占位)
    E6_COLORS[4],     # 蓝色
    E6_COLORS[5]      # 绿色
], dtype=np.float32)

def create_e6_palette():
    """创建E6专用调色板"""
    palette = []
    for color in E6_COLORS_WITH_SKIP.astype(np.uint8):
        palette.extend(color.tolist())
    # 填充到256色
    while len(palette) < 768:
        palette.extend([0, 0, 0])
    return palette

def find_nearest_color(pixel, colors=E6_COLORS):
    """找到最近的E6颜色"""
    pixel = np.asarray(pixel, dtype=np.float32)
    distances = np.sum((colors - pixel) ** 2, axis=1)
    return colors[np.argmin(distances)].astype(np.uint8)

def floyd_steinberg_dither(img_array):
    """Floyd-Steinberg抖动算法"""
    height, width = img_array.shape[:2]
    img_float = img_array.astype(np.float64).copy()
    
    # 误差分配系数
    error_coeffs = [(1, 0, 7/16), (-1, 1, 3/16), (0, 1, 5/16), (1, 1, 1/16)]
    
    for y in range(height):
        for x in range(width):
            old_pixel = np.clip(img_float[y, x], 0, 255)
            new_pixel = find_nearest_color(old_pixel)
            img_float[y, x] = new_pixel
            
            error = old_pixel - new_pixel
            
            # 分配误差到周围像素
            for dx, dy, coeff in error_coeffs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    img_float[ny, nx] = np.clip(img_float[ny, nx] + error * coeff, 0, 255)
    
    return img_float.astype(np.uint8)

def ordered_dither(img_array):
    """有序抖动（Bayer矩阵）"""
    height, width = img_array.shape[:2]
    
    # 4x4 Bayer矩阵
    bayer = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) * 16
    bayer_tiled = np.tile(bayer, (height // 4 + 1, width // 4 + 1))[:height, :width]
    
    # 添加抖动噪声
    dithered = np.clip(img_array.astype(np.float32) + bayer_tiled[:,:,np.newaxis] - 128, 0, 255)
    
    # 向量化量化
    result = dithered.reshape(-1, 3)
    for i in range(result.shape[0]):
        result[i] = find_nearest_color(result[i])
    
    return result.reshape(height, width, 3).astype(np.uint8)

def simple_quantize(img_array):
    """简单量化（无抖动）"""
    # 向量化处理
    shape = img_array.shape
    result = img_array.reshape(-1, 3)
    for i in range(result.shape[0]):
        result[i] = find_nearest_color(result[i])
    return result.reshape(shape).astype(np.uint8)

def validate_e6_colors(img_array):
    """验证并修正所有像素为有效的E6颜色"""
    height, width = img_array.shape[:2]
    result = img_array.reshape(-1, 3)
    
    # 向量化处理，更高效
    for i in range(result.shape[0]):
        result[i] = find_nearest_color(result[i])
    
    return result.reshape(height, width, 3)

def resize_image(img, target_w, target_h, mode):
    """统一的图像缩放函数"""
    if mode == 'fit':
        # 保持比例适应
        img.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
        # 创建白色背景并居中
        new_img = Image.new('RGB', (target_w, target_h), (255, 255, 255))
        left = (target_w - img.width) // 2
        top = (target_h - img.height) // 2
        new_img.paste(img, (left, top))
        return new_img
        
    elif mode == 'fill':
        # 填充整个区域（可能裁剪）
        img_ratio = img.width / img.height
        target_ratio = target_w / target_h
        
        if img_ratio > target_ratio:
            new_h = target_h
            new_w = int(target_h * img_ratio)
        else:
            new_w = target_w
            new_h = int(target_w / img_ratio)
        
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        # 裁剪中心区域
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        return img.crop((left, top, left + target_w, top + target_h))
        
    else:  # stretch
        # 拉伸到目标尺寸
        return img.resize((target_w, target_h), Image.Resampling.LANCZOS)

def test_firmware_compatibility(bmp_path):
    """测试BMP文件是否与固件完全兼容"""
    try:
        img = Image.open(bmp_path)
        pixels = np.array(img).reshape(-1, 3)
        total_pixels = len(pixels)
        
        # 向量化检查
        valid_mask = np.zeros(total_pixels, dtype=bool)
        for color in E6_COLORS.astype(np.uint8):
            valid_mask |= np.all(pixels == color, axis=1)
        
        incompatible_count = np.sum(~valid_mask)
        is_compatible = incompatible_count == 0
        
        if is_compatible:
            print(f'✓ 固件兼容性测试通过: 所有{total_pixels}个像素都是有效的E6颜色')
        else:
            print(f'✗ 固件兼容性测试失败: 发现{incompatible_count}个不兼容像素')
            if incompatible_count <= 10:
                invalid_indices = np.where(~valid_mask)[0][:10]
                img_shape = np.array(img).shape
                for idx in invalid_indices:
                    y, x = idx // img_shape[1], idx % img_shape[1]
                    r, g, b = pixels[idx]
                    print(f'  位置({x},{y}): RGB({r},{g},{b})')
        
        return is_compatible, incompatible_count
    except Exception as e:
        print(f'测试失败: {e}')
        return False, 0

def preprocess_image(img, config):
    """预处理图像"""
    # 确保RGB模式
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # 应用各种增强
    enhancements = [
        ('auto_balance', lambda i: ImageOps.autocontrast(i, cutoff=2), True),
        ('denoise', lambda i: i.filter(ImageFilter.MedianFilter(size=3)), False),
        ('color_enhance', lambda i, v: ImageEnhance.Color(i).enhance(v), 1.0),
        ('contrast', lambda i, v: ImageEnhance.Contrast(i).enhance(v), 1.0),
        ('brightness', lambda i, v: ImageEnhance.Brightness(i).enhance(v), 1.0),
        ('sharpen', lambda i, v: ImageEnhance.Sharpness(i).enhance(v) if v > 1.0 else i, 1.0),
        ('edge_enhance', lambda i: i.filter(ImageFilter.EDGE_ENHANCE), False)
    ]
    
    for key, func, default in enhancements:
        val = config.get(key, default)
        if key in ['auto_balance', 'denoise', 'edge_enhance']:
            if val:
                img = func(img)
        else:
            if val != default:
                img = func(img, val)
    
    return img

def optimize_colors(img_array):
    """优化颜色以适应6色显示"""
    result = img_array.astype(np.float32)
    
    # 向量化处理
    r, g, b = result[:,:,0], result[:,:,1], result[:,:,2]
    
    # 计算主色调
    max_vals = np.maximum(np.maximum(r, g), b)
    min_vals = np.minimum(np.minimum(r, g), b)
    
    # 增强纯色倾向的mask
    strong_color_mask = (max_vals - min_vals) > 80
    
    # 应用增强
    enhance_factor = 1.2
    reduce_factor = 0.85
    
    # 红色主导
    red_mask = strong_color_mask & (r == max_vals)
    result[red_mask, 0] = np.minimum(255, result[red_mask, 0] * enhance_factor)
    result[red_mask, 1:3] *= reduce_factor
    
    # 绿色主导
    green_mask = strong_color_mask & (g == max_vals) & ~red_mask
    result[green_mask, 1] = np.minimum(255, result[green_mask, 1] * enhance_factor)
    result[green_mask, 0] *= reduce_factor
    result[green_mask, 2] *= reduce_factor
    
    # 蓝色主导
    blue_mask = strong_color_mask & (b == max_vals) & ~red_mask & ~green_mask
    result[blue_mask, 2] = np.minimum(255, result[blue_mask, 2] * enhance_factor)
    result[blue_mask, 0:2] *= reduce_factor
    
    # 特殊颜色优化
    # 黄色
    yellow_mask = (r > 200) & (g > 200) & (b < 50)
    result[yellow_mask] = [255, 255, 0]
    
    # 红色
    pure_red_mask = (r > 200) & (g < 100) & (b < 100)
    result[pure_red_mask] = [255, 0, 0]
    
    # 绿色
    pure_green_mask = (r < 100) & (g > 200) & (b < 100)
    result[pure_green_mask] = [0, 255, 0]
    
    # 蓝色
    pure_blue_mask = (r < 100) & (g < 100) & (b > 200)
    result[pure_blue_mask] = [0, 0, 255]
    
    return np.clip(result, 0, 255).astype(np.uint8)

def process_single_image(input_file, args, config):
    """处理单个图像文件"""
    if not os.path.isfile(input_file):
        print(f'警告：文件 {input_file} 不存在，跳过')
        return False
    
    print(f'\n处理图像: {input_file}')
    print(f'预设: {args.preset}, 抖动: {args.method}')
    
    try:
        # 打开并转换为RGB
        img = Image.open(input_file).convert('RGB')
        original_size = img.size
        
        # 确定目标尺寸
        target_sizes = {
            'landscape': (800, 480),
            'portrait': (480, 800),
            'auto': (800, 480) if img.width > img.height else (480, 800)
        }
        target_w, target_h = target_sizes[args.dir]
        
        print(f'原始尺寸: {original_size[0]}x{original_size[1]}')
        print(f'目标尺寸: {target_w}x{target_h}')
        
        # 调整尺寸
        img = resize_image(img, target_w, target_h, args.mode)
        
        print('应用预处理...')
        img = preprocess_image(img, config)
        img_array = np.array(img, dtype=np.uint8)
        
        # 颜色优化
        if config.get('optimize_colors', True):
            print('优化颜色...')
            img_array = optimize_colors(img_array)
        
        # 应用量化
        print(f'应用{args.method}量化...')
        
        # 选择量化方法
        quantize_func = {
            'floyd': floyd_steinberg_dither,
            'ordered': ordered_dither,
            'none': simple_quantize
        }.get(args.method, simple_quantize)
        
        quantized = quantize_func(img_array)
        
        # 验证E6颜色（总是启用以确保固件兼容）
        quantized = validate_e6_colors(quantized)
        
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

# 处理输入
if os.path.isfile(args.input_path):
    # 单文件处理
    if not process_single_image(args.input_path, args, config):
        sys.exit(1)
elif os.path.isdir(args.input_path):
    # 批量处理
    print(f'扫描目录: {args.input_path}')
    
    # 查找图片文件
    extensions = ['jpg', 'jpeg', 'png', 'bmp']
    image_files = []
    for ext in extensions:
        for case in [ext.lower(), ext.upper()]:
            pattern = os.path.join(args.input_path, f'*.{case}')
            image_files.extend(glob.glob(pattern))
    
    image_files = sorted(set(image_files))  # 去重排序
    
    if not image_files:
        print(f'错误：未找到图片文件')
        sys.exit(1)
    
    print(f'找到 {len(image_files)} 个图片文件')
    print('-' * 60)
    
    # 批处理
    success_count = 0
    for i, f in enumerate(image_files, 1):
        print(f'\n[{i}/{len(image_files)}] ', end='')
        if process_single_image(f, args, config):
            success_count += 1
    
    print('\n' + '=' * 60)
    print(f'处理完成！成功: {success_count}/{len(image_files)} 个文件')
else:
    print(f'错误：{args.input_path} 无效路径')
    sys.exit(1)
