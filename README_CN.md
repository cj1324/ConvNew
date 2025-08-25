# E-Ink Spectra 6 显示屏图像转换器

专为7色电子墨水屏（Spectra 6）设计的图像转换工具，将普通图像转换为电子纸屏幕优化的有限调色板。

## 功能特性

- **7色调色板转换**：将图像转换为 Spectra 6 调色板（黑、白、红、黄、蓝、绿、橙）
- **多种抖动算法**：Floyd-Steinberg、有序抖动（Bayer）、无抖动
- **内容感知预设**：为照片、艺术品、文本和标志优化的设置
- **灵活的显示模式**：支持 800x480（横向）和 480x800（纵向）分辨率
- **智能缩放选项**：缩放、裁剪、填充或拉伸以适应显示尺寸
- **图像增强**：自动预处理，可调节对比度、亮度和锐度

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/ConvNew.git
cd ConvNew

# 安装依赖
pip install -e .
```

### 基本用法

```bash
# 使用默认设置转换图像（照片预设，Floyd-Steinberg 抖动）
python -m convnew.main image.jpg

# 使用特定预设
python -m convnew.main image.jpg --preset art

# 选择不同的抖动方法
python -m convnew.main image.jpg --method ordered

# 指定方向
python -m convnew.main image.jpg --dir portrait
```

### 命令行选项

| 选项 | 可选值 | 默认值 | 描述 |
|------|--------|--------|------|
| `--preset` | photo, art, text, logo | photo | 内容类型优化 |
| `--method` | floyd, ordered, none | floyd | 抖动算法 |
| `--dir` | landscape, portrait, auto | auto | 显示方向 |
| `--mode` | scale, cut, fill, stretch | scale | 图像适配方法 |

## 预设说明

### Photo（照片）
最适合照片和自然图像
- 平衡的色彩增强
- 适度的对比度调整
- 自然的抖动效果

### Art（艺术）
优化用于艺术作品和插图
- 增强的色彩活力
- 提高饱和度
- 强边缘保留

### Text（文本）
适用于文档和文字密集的图像
- 最大对比度
- 锐利的边缘增强
- 最小的颜色处理

### Logo（标志）
完美适用于图形和标志
- 最大色彩饱和度
- 高对比度
- 清晰的颜色分离

## 抖动方法

### Floyd-Steinberg
误差扩散算法，将量化误差分配到邻近像素，创建平滑的渐变和自然的图像。

### Ordered（有序）
使用重复的阈值矩阵模式，创建独特的交叉阴影外观。适合图形和文本。

### None（无）
直接颜色量化，无抖动。最适合纯色图像或需要海报化效果时使用。

## 输出文件

转换器生成两个文件：
- `*_spectra6.bmp`：用于电子墨水屏显示的7色BMP文件
- `*_preview.png`：用于在普通屏幕上验证的PNG预览

## 构建可执行文件（Windows）

```powershell
# 使用提供的构建脚本
./build_exe.ps1

# 或手动使用 PyInstaller
pyinstaller --onefile --name ConvNew ./convnew/main.py
```

## 项目结构

```
ConvNew/
├── convnew/           # 主转换器包
│   ├── __init__.py   
│   └── main.py       # 核心转换逻辑
├── backup/           # 旧版转换器文件
├── build/            # 构建产物
├── dist/             # 发布包
├── build_exe.ps1     # Windows 构建脚本
├── pyproject.toml    # 项目配置
├── README.md         # 英文说明
└── README_CN.md      # 本文件
```

## 系统要求

- Python 3.7+
- Pillow >= 10.0.0
- NumPy >= 1.24.0
- SciPy >= 1.11.0
- scikit-learn >= 1.3.0
- Numba >= 0.58.0（可选）

## 调色板

Spectra 6 电子墨水屏支持正好7种颜色：

| 颜色 | RGB 值 | 十六进制 |
|------|--------|----------|
| 黑色 | (0, 0, 0) | #000000 |
| 白色 | (255, 255, 255) | #FFFFFF |
| 红色 | (255, 0, 0) | #FF0000 |
| 黄色 | (255, 255, 0) | #FFFF00 |
| 蓝色 | (0, 0, 255) | #0000FF |
| 绿色 | (0, 255, 0) | #00FF00 |
| 橙色 | (255, 128, 0) | #FF8000 |

## 使用示例

```bash
# 使用最佳设置转换照片
python -m convnew.main vacation.jpg --preset photo

# 转换文档以获得最大可读性
python -m convnew.main document.pdf --preset text --method none

# 转换具有鲜艳色彩的标志
python -m convnew.main logo.png --preset logo --method ordered

# 书籍封面的纵向模式
python -m convnew.main book_cover.jpg --dir portrait --mode fill
```

## 故障排除

### 常见问题

**问题**：颜色看起来不对或褪色
- **解决方案**：尝试不同的预设或调整抖动方法

**问题**：文字难以阅读
- **解决方案**：使用 `text` 预设配合 `none` 抖动方法

**问题**：图像不能正确适应显示屏
- **解决方案**：尝试不同的 `--mode` 选项（scale、cut、fill、stretch）

**问题**：图像中有太多噪点或颗粒
- **解决方案**：尝试 `ordered` 抖动而不是 `floyd`

## 高级用法

### 批量处理

处理多个图像：

```bash
# Linux/Mac
for img in *.jpg; do
    python -m convnew.main "$img" --preset photo
done

# Windows (PowerShell)
Get-ChildItem *.jpg | ForEach-Object {
    python -m convnew.main $_.FullName --preset photo
}
```

### 自定义集成

```python
from convnew.main import process_image

# 以编程方式处理图像
result = process_image(
    input_path="image.jpg",
    preset="photo",
    method="floyd",
    direction="landscape",
    mode="scale"
)
```

## 贡献

欢迎贡献！请随时提交问题或拉取请求。

### 开发设置

```bash
# 以开发模式安装
pip install -e .

# 运行测试（如果可用）
python -m pytest tests/
```

## 许可证

本项目是开源的，采用 MIT 许可证。

## 致谢

- 专为 Spectra 6 7色电子墨水屏设计
- Floyd-Steinberg 抖动算法由 Robert W. Floyd 和 Louis Steinberg 提出
- Bayer 有序抖动矩阵由 Bryce Bayer 提出

## 支持

如有问题、疑问或建议，请在 GitHub 上开启 issue 或联系维护者。

---

为电子墨水爱好者用 ❤️ 制作