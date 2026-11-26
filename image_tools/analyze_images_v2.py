from PIL import Image
import os

def detect_sections(filepath):
    """Detect layout sections by scanning rows and columns for black/dark content"""
    img = Image.open(filepath).convert('RGBA')
    w, h = img.size
    
    # Scan each row - what % is dark content (brightness < 128)?
    row_darkness = []
    for y in range(h):
        dark_pixels = 0
        total = 0
        for x in range(w):
            r, g, b, a = img.getpixel((x, y))
            if a > 128:
                total += 1
                if 0.299*r + 0.587*g + 0.114*b < 128:
                    dark_pixels += 1
        row_darkness.append(dark_pixels / max(total, 1) * 100)
    
    # Find rows with significant content (>10% dark pixels)
    content_rows = [y for y, pct in enumerate(row_darkness) if pct > 10]
    
    # Detect horizontal bands
    bands = []
    if content_rows:
        start = content_rows[0]
        prev = start
        for y in content_rows[1:]:
            if y - prev > 5:  # gap of more than 5px = new band
                bands.append((start, prev))
                start = y
            prev = y
        bands.append((start, prev))
    
    return {
        'height': h,
        'width': w,
        'content_bands': bands,
        'dark_row_count': len(content_rows),
        'dark_pct_total': sum(row_darkness) / h,
    }

def classify_area(filepath):
    """Classify into regions and detect primary elements"""
    img = Image.open(filepath).convert('RGBA')
    w, h = img.size
    
    # Sample grid 20x20 to detect patterns
    grid_w, grid_h = 20, 20
    cell_w, cell_h = w // grid_w, h // grid_h
    
    regions = []
    for gy in range(grid_h):
        for gx in range(grid_w):
            # Sample center of cell
            sx, sy = gx * cell_w + cell_w//2, gy * cell_h + cell_h//2
            r, g, b, a = img.getpixel((sx, sy))
            if a < 128:
                regions.append('transparent')
            else:
                bright = 0.299*r + 0.587*g + 0.114*b
                if bright > 220:
                    regions.append('white')
                elif bright > 150:
                    regions.append('light')
                elif bright > 80:
                    regions.append('gray')
                else:
                    regions.append('dark')
    
    # Count regions
    counts = {}
    for r in regions:
        counts[r] = counts.get(r, 0) + 1
    
    return counts

# Look for red accent pixels (common in Tesla branding/buttons)
def find_red_accents(filepath):
    img = Image.open(filepath).convert('RGBA')
    w, h = img.size
    red_pixels = 0
    total_opaque = 0
    red_clusters = []
    
    for y in range(h):
        for x in range(w):
            r, g, b, a = img.getpixel((x, y))
            if a > 128:
                total_opaque += 1
                if r > 180 and g < 80 and b < 80:
                    red_pixels += 1
                    red_clusters.append((x, y))
    
    return {
        'red_pixels': red_pixels,
        'red_pct': round(red_pixels / max(total_opaque, 1) * 100, 2),
        'has_red': red_pixels > 50,
        'red_clusters': len(red_clusters)
    }

def analyze_horizontal_distribution(filepath):
    """Vertical scanning - detect left sidebar vs main content patterns"""
    img = Image.open(filepath).convert('RGBA')
    w, h = img.size
    
    # Sample several horizontal strips
    strips = {
        'top_25pct': range(0, h//4),
        'mid_top': range(h//4, h//2),
        'mid_bottom': range(h//2, 3*h//4),
        'bottom_25pct': range(3*h//4, h)
    }
    
    results = {}
    for name, y_range in strips.items():
        left_dark = 0
        right_dark = 0
        left_total = 0
        right_total = 0
        mid_w = w // 2
        
        for y in y_range:
            for x in range(w):
                r, g, b, a = img.getpixel((x, y))
                if a > 128:
                    bright = 0.299*r + 0.587*g + 0.114*b
                    is_dark = bright < 128
                    if x < mid_w:
                        left_total += 1
                        if is_dark: left_dark += 1
                    else:
                        right_total += 1
                        if is_dark: right_dark += 1
        
        results[name] = {
            'left_dark_pct': round(left_dark / max(left_total, 1) * 100, 1),
            'right_dark_pct': round(right_dark / max(right_total, 1) * 100, 1)
        }
    
    return results

files = ['tsla1.png', 'tsla2.png', 'tsla3.png', 'tsla4.png', 'tsla5.png', 'tsla6.png']
base = 'ref_photos'

for f in files:
    path = os.path.join(base, f)
    print(f"\n{'='*70}")
    print(f"  IMAGE: {f}")
    print(f"{'='*70}")
    
    # Layout analysis
    sections = detect_sections(path)
    print(f"\n  --- Layout Analysis ---")
    print(f"  Dimensions: {sections['width']}x{sections['height']}")
    print(f"  Content bands (y-ranges with dark content): {sections['content_bands']}")
    print(f"  Overall darkness: {sections['dark_pct_total']:.1f}%")
    
    # Red accents
    red = find_red_accents(path)
    print(f"\n  --- Color Analysis ---")
    print(f"  Red accent pixels: {red['red_pixels']} ({red['red_pct']}%)")
    
    # Region classification
    regions = classify_area(path)
    total_regions = sum(regions.values())
    print(f"  Region composition (200-cell grid):")
    for k in ['white', 'light', 'gray', 'dark', 'transparent']:
        if k in regions:
            print(f"    {k}: {regions[k]/total_regions*100:.1f}%")
    
    # Horizontal distribution
    dist = analyze_horizontal_distribution(path)
    print(f"\n  --- Left/Right Distribution (dark content %) ---")
    for strip, data in dist.items():
        print(f"    {strip}: Left={data['left_dark_pct']}% | Right={data['right_dark_pct']}%")