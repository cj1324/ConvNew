# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an image conversion tool for E Ink Spectra 6 7-color displays. The project converts regular images into a 7-color palette (black, white, red, yellow, blue, green, orange) optimized for e-ink displays with 800x480 or 480x800 resolution.

## Core Components

### Main Modules
- `convert.py`: Basic image converter with simple palette quantization
- `convnew/main.py`: Advanced converter with multiple dithering algorithms and image preprocessing

### Key Algorithms
- **Floyd-Steinberg Dithering**: Error diffusion algorithm for smooth color transitions
- **Ordered Dithering**: Bayer matrix-based dithering for pattern-based quantization
- **Color Optimization**: Enhances pure color tendencies for better 7-color display

## Development Commands

### Python Environment
```bash
# Install dependencies
pip install -r requirements.txt
# Or install from pyproject.toml
pip install -e .

# Run the basic converter
python convert.py <image_file> [--dir landscape|portrait] [--mode scale|cut] [--dither 0|3]

# Run the advanced converter with presets
python convnew/main.py <image_file> [--preset photo|art|text|logo] [--method floyd|ordered|none]
```

### Building Executable (Windows)
```bash
# Using PowerShell script
./build_exe.ps1

# Or directly with PyInstaller
pyinstaller --onefile --name convert_main ./convnew/main.py
```

### Batch Processing (Windows)
```bash
# Convert all images in current directory
converterTo7color_all.cmd
```

## Architecture & Implementation Details

### Color Processing Pipeline
1. **Image Loading & Resizing**: Handles orientation (landscape/portrait) and scaling modes (fit/fill/stretch)
2. **Preprocessing**: Applies contrast, brightness, sharpness, and color enhancements based on presets
3. **Color Optimization**: Enhances main color channels to better match the 7-color palette
4. **Quantization**: Maps pixels to nearest Spectra 6 colors using selected dithering method
5. **Output**: Saves as BMP for e-ink display and PNG for preview

### Spectra 6 Color Palette
The standard 7-color e-ink palette is hardcoded in `SPECTRA6_COLORS`:
- Black: [0, 0, 0]
- White: [255, 255, 255]
- Red: [255, 0, 0]
- Yellow: [255, 255, 0]
- Blue: [0, 0, 255]
- Green: [0, 255, 0]
- Orange: [255, 128, 0]

### Preset Configurations
Located in `convnew/main.py`, presets optimize parameters for different content types:
- **photo**: Balanced enhancement for photographs
- **art**: High color enhancement for artwork
- **text**: High contrast and edge enhancement for documents
- **logo**: Maximum color saturation for graphics

## Testing

No formal test suite exists. Manual testing involves:
```bash
# Test basic conversion
python convert.py test_image.jpg

# Test different presets
python convnew/main.py test_image.jpg --preset photo
python convnew/main.py test_image.jpg --preset art --method ordered

# Compare outputs in *_output.bmp and *_spectra6.bmp files
```

## Dependencies

Core dependencies (from pyproject.toml):
- Pillow >= 10.0.0 (image processing)
- numpy >= 1.24.0 (array operations)
- numba >= 0.58.0 (JIT compilation, though not actively used)
- scipy >= 1.11.0 (scientific computing)
- scikit-learn >= 1.3.0 (machine learning utilities)

## Key Implementation Notes

- All images are converted to RGB mode before processing to ensure consistency
- The Floyd-Steinberg implementation uses float64 for stability and clips values to prevent overflow
- Output files follow naming convention: `<input>_output.bmp` (basic) or `<input>_spectra6.bmp` (advanced)
- Both converters maintain aspect ratio options and support 800x480 (landscape) or 480x800 (portrait) displays