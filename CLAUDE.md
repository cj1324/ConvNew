# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an image conversion tool for E Ink Spectra 6 7-color displays. The project converts regular images into a 7-color palette (black, white, red, yellow, blue, green, orange) optimized for e-ink displays with 800x480 or 480x800 resolution.

## Project Structure

```
ConvNew/
├── convnew/                 # Main converter package
│   ├── __init__.py         # Package initialization
│   └── main.py             # Advanced converter with multiple algorithms
├── backup/                  # Legacy converter files
│   ├── convert.py          # Basic image converter (deprecated)
│   └── converterTo7color_all.cmd  # Batch processing script
├── build/                   # Build artifacts directory
├── dist/                    # Distribution packages
├── build_exe.ps1           # Windows executable build script
├── pyproject.toml          # Project configuration and dependencies
├── CLAUDE.md               # This file - AI assistant instructions
└── README.md               # Project documentation
```

## Core Components

### Main Module (convnew/main.py)
Advanced converter with:
- Multiple dithering algorithms (Floyd-Steinberg, Ordered, None)
- Image preprocessing with presets (photo, art, text, logo)
- Color optimization for 7-color e-ink displays
- Automatic orientation detection and scaling

### Legacy Module (backup/convert.py)
Basic converter with simple palette quantization (kept for reference/compatibility)

## Key Algorithms

### Dithering Methods
- **Floyd-Steinberg Dithering**: Error diffusion algorithm for smooth color transitions
- **Ordered Dithering**: Bayer matrix-based dithering for pattern-based quantization
- **No Dithering**: Direct color quantization without error diffusion

### Color Processing Pipeline
1. **Image Loading**: Handles various formats via Pillow
2. **Resizing**: Supports landscape (800x480) and portrait (480x800) modes
3. **Preprocessing**: Applies enhancements based on content type
4. **Color Optimization**: Enhances pure color tendencies
5. **Quantization**: Maps to Spectra 6 palette using selected method
6. **Output**: Saves as BMP for e-ink and PNG for preview

## Development Commands

### Python Environment Setup
```bash
# Install dependencies from pyproject.toml
pip install -e .

# Or install requirements directly
pip install Pillow numpy numba scipy scikit-learn
```

### Running the Converter
```bash
# Run the advanced converter with default settings
python -m convnew.main <image_file>

# With specific preset and method
python -m convnew.main <image_file> --preset photo --method floyd

# Available options:
# --preset: photo, art, text, logo (default: photo)
# --method: floyd, ordered, none (default: floyd)
# --dir: landscape, portrait, auto (default: auto)
# --mode: scale, cut, fill, stretch (default: scale)
```

### Building Windows Executable
```bash
# Using PowerShell script
./build_exe.ps1

# Or directly with PyInstaller
pyinstaller --onefile --name ConvNew --path ./convnew ./convnew/main.py
```

### Batch Processing (Windows)
```bash
# Convert all images in current directory (legacy)
cd backup
converterTo7color_all.cmd
```

## Spectra 6 Color Palette

The standard 7-color e-ink palette is defined as:
```python
SPECTRA6_COLORS = np.array([
    [0, 0, 0],       # Black
    [255, 255, 255], # White
    [255, 0, 0],     # Red
    [255, 255, 0],   # Yellow
    [0, 0, 255],     # Blue
    [0, 255, 0],     # Green
    [255, 128, 0]    # Orange
], dtype=np.uint8)
```

## Preset Configurations

Located in `convnew/main.py`, each preset optimizes for different content:

### Photo Preset
- Balanced enhancement for photographs
- Moderate contrast and sharpness
- Natural color optimization

### Art Preset
- High color enhancement for artwork
- Increased saturation and vibrancy
- Stronger edge enhancement

### Text Preset
- Maximum contrast for readability
- Strong edge enhancement
- Minimal color optimization

### Logo Preset
- Maximum color saturation
- Strong contrast
- Preserves graphic elements

## Testing Guidelines

### Manual Testing
```bash
# Test basic conversion
python -m convnew.main test_image.jpg

# Test all presets
for preset in photo art text logo; do
    python -m convnew.main test_image.jpg --preset $preset
done

# Test different methods
for method in floyd ordered none; do
    python -m convnew.main test_image.jpg --method $method
done

# Output files: *_spectra6.bmp and *_preview.png
```

### Expected Output
- `*_spectra6.bmp`: 7-color BMP for e-ink display
- `*_preview.png`: PNG preview for verification
- Files should contain only the 7 Spectra 6 colors
- Aspect ratio should be maintained or adapted to display dimensions

## Dependencies

Core dependencies (from pyproject.toml):
- **Pillow >= 10.0.0**: Image processing and I/O
- **numpy >= 1.24.0**: Array operations and color calculations
- **numba >= 0.58.0**: JIT compilation (optional optimization)
- **scipy >= 1.11.0**: Scientific computing utilities
- **scikit-learn >= 1.3.0**: Machine learning utilities (for future features)

## Implementation Notes

### Performance Considerations
- Floyd-Steinberg uses float64 for numerical stability
- Error diffusion is applied with proper boundary checking
- Images are processed in RGB mode for consistency

### File Naming Convention
- Input: `image.jpg`
- Output: `image_spectra6.bmp` (e-ink format)
- Preview: `image_preview.png` (optional preview)

### Aspect Ratio Handling
- **scale**: Fit image within display bounds, maintain ratio
- **cut**: Center crop to fill display
- **fill**: Fit with padding (letterbox/pillarbox)
- **stretch**: Distort to exact display dimensions

## Future Improvements

Potential enhancements to consider:
- GUI interface for easier parameter adjustment
- Real-time preview of conversion results
- Custom color palette support
- Advanced dithering algorithms (Atkinson, Sierra)
- Batch processing with progress tracking
- Color profile management for different e-ink models

## Troubleshooting

Common issues and solutions:
- **Memory errors**: Reduce image size before processing
- **Color artifacts**: Try different presets or dithering methods
- **Poor text readability**: Use text preset with no dithering
- **Loss of detail**: Adjust preprocessing parameters in preset

## Important Reminders

- Always test changes with various image types
- Maintain backward compatibility with legacy convert.py if possible
- Document any new parameters or features
- Keep output format compatible with Spectra 6 displays
- Preserve the 7-color limitation strictly