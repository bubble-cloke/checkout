from PIL import Image
import os

def extract_ui_elements(filepath):
    img = Image.open(filepath).convert('RGBA')
    w, h = img.size
    
    # Detect the sidebar boundary in tsla1 and tsla2
    mid_y = h // 2
    sidebar_x = None
    for x in range(0, w):
        dark_count = 0
        for yy in range(mid_y-50, mid_y+50):
            r, g, b, a = img.getpixel((x, yy))
            if a > 128 and (0.299*r + 0.587*g + 0.114*b) < 128:
                dark_count += 1
        if dark_count > 60:
            sidebar_x = x
    
    if sidebar_x is not None:
        sidebar_width = sidebar_x + 1
    else:
        sidebar_width = None
    
    # Find bottom red buttons
    red_px = []
    for yy in range(h-150, h):
        for xx in range(0, w):
            r, g, b, a = img.getpixel((xx, yy))
            if a > 128 and r > 180 and g < 80 and b < 80:
                red_px.append((xx, yy))
    
    red_info = None
    if red_px:
        xs = [x for x,_ in red_px]
        ys = [y for _,y in red_px]
        red_info = {
            'left': min(xs),
            'right': max(xs),
            'top': min(ys),
            'bottom': max(ys),
            'width': max(xs) - min(xs),
            'height': max(ys) - min(ys)
        }
    
    # Find horizontal dividers (lines spanning >70% width that are not white)
    h_lines = []
    for yy in range(h):
        line_pixels = 0
        for xx in range(0, w, 2):
            r, g, b, a = img.getpixel((xx, yy))
            if a > 128:
                bright = 0.299*r + 0.587*g + 0.114*b
                if bright < 200:
                    line_pixels += 1
        if line_pixels > w * 0.7 * 0.5:  # 70% of sampled pixels are non-white
            h_lines.append(yy)
    
    if h_lines:
        collapsed = [h_lines[0]]
        for line in h_lines[1:]:
            if line - collapsed[-1] > 3:
                collapsed.append(line)
        h_lines = collapsed[:10]
    
    return {
        'sidebar_width': sidebar_width,
        'red_button': red_info,
        'horizontal_lines': h_lines,
    }

# Also scan for text-like content bands (rows with high contrast transitions)
def find_content_regions(filepath):
    img = Image.open(filepath).convert('RGBA')
    w, h = img.size
    
    # For each row, count non-white, non-transparent pixels
    bands = []
    in_band = False
    band_start = 0
    
    for y in range(h):
        content_count = 0
        for x in range(0, w, 4):
            r, g, b, a = img.getpixel((x, y))
            if a > 128:
                bright = 0.299*r + 0.587*g + 0.114*b
                if bright < 200:  # non-white content
                    content_count += 1
        
        has_content = content_count > 10
        if has_content and not in_band:
            in_band = True
            band_start = y
        elif not has_content and in_band:
            in_band = False
            bands.append((band_start, y-1))
    
    if in_band:
        bands.append((band_start, h-1))
    
    return bands

files = ['tsla1.png', 'tsla2.png', 'tsla3.png', 'tsla4.png', 'tsla5.png', 'tsla6.png']
base = 'ref_photos'

for f in files:
    path = os.path.join(base, f)
    print(f"\n{'='*70}")
    print(f"  {f}")
    print(f"{'='*70}")
    
    try:
        elements = extract_ui_elements(path)
        bands = find_content_regions(path)
        
        if elements['sidebar_width']:
            print(f"  \n  SIDEBAR: ~{elements['sidebar_width']}px wide")
        if elements['red_button']:
            rb = elements['red_button']
            print(f"  \n  RED BUTTON:")
            print(f"    Position: ({rb['left']}, {rb['top']}) to ({rb['right']}, {rb['bottom']})")
            print(f"    Size: {rb['width']} x {rb['height']}px")
            print(f"    Centered at x={rb['left'] + rb['width']//2}")
        if elements['horizontal_lines']:
            print(f"  \n  HORIZONTAL DIVIDERS at y: {elements['horizontal_lines']}")
        
        print(f"  \n  CONTENT REGIONS (y-ranges):")
        for start, end in bands:
            height = end - start + 1
            pct_from_top = round(start / bands[-1][1] * 100, 1) if bands else 0
            print(f"    y={start}-{end} ({height}px tall)")
        
        print(f"  \n  IMAGE BOUNDS: {Image.open(path).size}")
        
    except Exception as e:
        print(f"  Error: {e}")