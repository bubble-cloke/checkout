from PIL import Image

img = Image.open('cars_images/modely.avif').convert('RGB')
w, h = img.size
pixels = img.load()

for y in range(h):
    for x in range(w):
        r, g, b = pixels[x, y]
        # If pixel is close to white (background), make it black
        if r > 240 and g > 240 and b > 240:
            pixels[x, y] = (0, 0, 0)
        # If pixel is a light gray edge (anti-aliased), darken it
        elif r > 200 and g > 200 and b > 200:
            pixels[x, y] = (int(r * 0.5), int(g * 0.5), int(b * 0.5))

img.save('cars_images/modely.avif', format='AVIF')
print('Done - modely.avif now has dark background matching other images')