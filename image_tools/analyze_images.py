from PIL import Image
import os
from collections import Counter

def analyze_image(filepath):
    img = Image.open(filepath).convert('RGBA')
    width, height = img.size
    
    # Get pixel data
    pixels = list(img.getdata())
    
    # Count colors (quantized to reduce noise)
    quantized = [(r//32*32, g//32*32, b//32*32, a//64*64) for r,g,b,a in pixels]
    color_counts = Counter(quantized)
    
    # Top 10 most common colors
    top_colors = color_counts.most_common(10)
    
    # Check for transparency
    has_transparency = any(a < 255 for r,g,b,a in pixels)
    transparent_pixels = sum(1 for r,g,b,a in pixels if a < 255)
    transparency_pct = (transparent_pixels / len(pixels)) * 100
    
    # Analyze edges/contrast (simple brightness analysis)
    brightnesses = [0.299*r + 0.587*g + 0.114*b for r,g,b,a in pixels if a > 128]
    if brightnesses:
        avg_brightness = sum(brightnesses) / len(brightnesses)
        # Split into quadrants to detect layout
        half_w, half_h = width // 2, height // 2
        quadrants = {
            'top-left': [],
            'top-right': [],
            'bottom-left': [],
            'bottom-right': []
        }
        for y in range(height):
            for x in range(width):
                r, g, b, a = img.getpixel((x, y))
                if a > 128:
                    bright = 0.299*r + 0.587*g + 0.114*b
                    if y < half_h and x < half_w:
                        quadrants['top-left'].append(bright)
                    elif y < half_h and x >= half_w:
                        quadrants['top-right'].append(bright)
                    elif y >= half_h and x < half_w:
                        quadrants['bottom-left'].append(bright)
                    else:
                        quadrants['bottom-right'].append(bright)
        
        quadrant_avg = {k: sum(v)/len(v) if v else 0 for k,v in quadrants.items()}
    else:
        avg_brightness = 0
        quadrant_avg = {}
    
    return {
        'size': f"{width}x{height}",
        'has_transparency': has_transparency,
        'transparency_pct': round(transparency_pct, 1),
        'avg_brightness': round(avg_brightness, 1),
        'quadrant_brightness': {k: round(v, 1) for k,v in quadrant_avg.items()},
        'top_colors': [(f"rgb({r},{g},{b})", c) for (r,g,b,a), c in top_colors[:5]],
        'total_pixels': len(pixels),
        'file_size_kb': os.path.getsize(filepath) // 1024
    }

files = ['tsla1.png', 'tsla2.png', 'tsla3.png', 'tsla4.png', 'tsla5.png', 'tsla6.png']
base = 'ref_photos'

for f in files:
    path = os.path.join(base, f)
    print(f"\n{'='*60}")
    print(f"  {f}")
    print(f"{'='*60}")
    try:
        info = analyze_image(path)
        print(f"  Dimensions: {info['size']}")
        print(f"  File Size: {info['file_size_kb']} KB")
        print(f"  Has Transparency: {info['has_transparency']} ({info['transparency_pct']}% transparent)")
        print(f"  Average Brightness: {info['avg_brightness']}/255")
        print(f"  Quadrant Brightness (TL/TR/BL/BR): {info['quadrant_brightness']}")
        print(f"  Top Colors:")
        for color, count in info['top_colors']:
            pct = round(count / info['total_pixels'] * 100, 1)
            print(f"    {color}: {pct}%")
    except Exception as e:
        print(f"  ERROR: {e}")