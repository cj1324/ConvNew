# Image Converter for E-Ink E6 Display

A specialized image conversion tool designed for 6-color e-ink displays (E6), converting regular images into a limited color palette optimized for e-paper screens.

## Features

- **6-Color Palette Conversion**: Converts images to the E6 palette (Black, White, Yellow, Red, Blue, Green)
- **Multiple Dithering Algorithms**: Floyd-Steinberg, Ordered (Bayer), and None
- **Content-Aware Presets**: Optimized settings for photos, artwork, text, and logos
- **Flexible Display Modes**: Support for both 800x480 (landscape) and 480x800 (portrait) resolutions
- **Smart Scaling Options**: Scale, crop, fill, or stretch to fit display dimensions
- **Image Enhancement**: Automatic preprocessing with adjustable contrast, brightness, and sharpness

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ConvNew.git
cd ConvNew

# Install dependencies
pip install -e .
```

### Basic Usage

```bash
# Convert an image with default settings (photo preset, Floyd-Steinberg dithering)
python -m convnew.main image.jpg

# Use a specific preset
python -m convnew.main image.jpg --preset art

# Choose a different dithering method
python -m convnew.main image.jpg --method ordered

# Specify orientation
python -m convnew.main image.jpg --dir portrait
```

### Command Line Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--preset` | photo, art, text, logo | photo | Content-type optimization |
| `--method` | floyd, ordered, none | floyd | Dithering algorithm |
| `--dir` | landscape, portrait, auto | auto | Display orientation |
| `--mode` | scale, cut, fill, stretch | scale | Image fitting method |

## Presets Explained

### Photo
Best for photographs and natural images
- Balanced color enhancement
- Moderate contrast adjustment
- Natural-looking dithering

### Art
Optimized for artwork and illustrations
- Enhanced color vibrancy
- Increased saturation
- Strong edge preservation

### Text
Ideal for documents and text-heavy images
- Maximum contrast
- Sharp edge enhancement
- Minimal color processing

### Logo
Perfect for graphics and logos
- Maximum color saturation
- High contrast
- Clean color separation

## Dithering Methods

### Floyd-Steinberg
Error diffusion algorithm that distributes quantization errors to neighboring pixels, creating smooth gradients and natural-looking images.

### Ordered (Bayer)
Uses a repeating threshold matrix pattern, creating a distinctive crosshatch appearance. Good for graphics and text.

### None
Direct color quantization without dithering. Best for images with solid colors or when a posterized effect is desired.

## Output Files

The converter generates two files:
- `*_e6.bmp`: 6-color BMP file ready for e-ink display
- `*_preview.png`: PNG preview for verification on regular screens

## Building Executable (Windows)

```powershell
# Using the provided build script
./build_exe.ps1

# Or manually with PyInstaller
pyinstaller --onefile --name ConvNew ./convnew/main.py
```

## Project Structure

```
ConvNew/
├── convnew/           # Main converter package
│   ├── __init__.py   
│   └── main.py       # Core conversion logic
├── backup/           # Legacy converter files
├── build/            # Build artifacts
├── dist/             # Distribution packages
├── build_exe.ps1     # Windows build script
├── pyproject.toml    # Project configuration
└── README.md         # This file
```

## Requirements

- Python 3.7+
- Pillow >= 10.0.0
- NumPy >= 1.24.0
- SciPy >= 1.11.0
- scikit-learn >= 1.3.0
- Numba >= 0.58.0 (optional)

## Color Palette

The E6 e-ink display supports exactly 6 colors:

| Color | RGB Values | Hex |
|-------|------------|-----|
| Black | (0, 0, 0) | #000000 |
| White | (255, 255, 255) | #FFFFFF |
| Yellow | (255, 243, 56) | #FFF338 |
| Red | (191, 0, 0) | #BF0000 |
| Blue | (100, 64, 255) | #6440FF |
| Green | (67, 138, 28) | #438A1C |

## Examples

```bash
# Convert a photo with optimal settings
python -m convnew.main vacation.jpg --preset photo

# Convert a document for maximum readability
python -m convnew.main document.pdf --preset text --method none

# Convert a logo with vibrant colors
python -m convnew.main logo.png --preset logo --method ordered

# Portrait mode for book covers
python -m convnew.main book_cover.jpg --dir portrait --mode fill
```

## Troubleshooting

### Common Issues

**Problem**: Colors look wrong or washed out
- **Solution**: Try different presets or adjust the dithering method

**Problem**: Text is hard to read
- **Solution**: Use the `text` preset with `none` dithering method

**Problem**: Image doesn't fit the display properly
- **Solution**: Experiment with different `--mode` options (scale, cut, fill, stretch)

**Problem**: Too much noise or grain in the image
- **Solution**: Try `ordered` dithering instead of `floyd`

## Advanced Usage

### Batch Processing

For processing multiple images:

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

### Custom Integration

```python
from convnew.main import process_image

# Process an image programmatically
result = process_image(
    input_path="image.jpg",
    preset="photo",
    method="floyd",
    direction="landscape",
    mode="scale"
)
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

### Development Setup

```bash
# Install in development mode
pip install -e .

# Run tests (when available)
python -m pytest tests/
```

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Designed specifically for E6 6-color e-ink displays
- Floyd-Steinberg dithering algorithm by Robert W. Floyd and Louis Steinberg
- Bayer ordered dithering matrix by Bryce Bayer

## Support

For issues, questions, or suggestions, please open an issue on GitHub or contact the maintainers.

---

Made with ❤️ for e-ink enthusiasts