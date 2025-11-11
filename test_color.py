#!/usr/bin/env python3
#encoding: utf-8

from PIL import Image, ImageDraw
import numpy as np

# Create a test image with colored rectangles
img = Image.new('RGB', (800, 480), 'white')
draw = ImageDraw.Draw(img)

# Draw colored rectangles to test all 6 colors
colors = [
    ((0, 0, 100, 120), (255, 0, 0)),      # Red
    ((100, 0, 200, 120), (0, 255, 0)),    # Green  
    ((200, 0, 300, 120), (0, 0, 255)),    # Blue
    ((300, 0, 400, 120), (255, 255, 0)),  # Yellow
    ((400, 0, 500, 120), (0, 0, 0)),      # Black
    ((500, 0, 600, 120), (255, 255, 255)) # White
]

for rect, color in colors:
    draw.rectangle(rect, fill=color)

# Add text labels
for i, (rect, color) in enumerate(colors):
    x = rect[0] + 10
    y = rect[3] + 10
    draw.text((x, y), str(color), fill='black')

img.save('test_colors.jpg')
print('Test image created: test_colors.jpg')