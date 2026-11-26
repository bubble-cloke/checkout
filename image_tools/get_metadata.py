import struct, os

def get_png_info(filepath):
    with open(filepath, 'rb') as f:
        # Check PNG signature
        sig = f.read(8)
        if sig != b'\x89PNG\r\n\x1a\n':
            return None, None, None
        # Read IHDR chunk
        f.read(4)  # chunk length
        f.read(4)  # chunk type
        width = struct.unpack('>I', f.read(4))[0]
        height = struct.unpack('>I', f.read(4))[0]
        bit_depth = struct.unpack('B', f.read(1))[0]
        color_type = struct.unpack('B', f.read(1))[0]
        color_modes = {0: 'Grayscale', 2: 'RGB', 3: 'Indexed', 4: 'Grayscale+Alpha', 6: 'RGBA'}
        return width, height, color_modes.get(color_type, f'Unknown({color_type})')

files = ['tsla1.png', 'tsla2.png', 'tsla3.png', 'tsla4.png', 'tsla5.png', 'tsla6.png']
base = 'ref_photos'

print(f"{'File':<12} {'Size':<8} {'Width':<8} {'Height':<8} {'Color Mode':<20}")
print("-" * 56)
for f in files:
    path = os.path.join(base, f)
    size_kb = os.path.getsize(path) // 1024
    w, h, cm = get_png_info(path)
    print(f"{f:<12} {size_kb}KB    {w:<8} {h:<8} {cm:<20}")