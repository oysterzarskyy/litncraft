from PIL import Image, ImageDraw
import math

BLOCK_SIZE = 32
UI_SIZE = 64

# utility helpers

def clamp(value, minimum=0, maximum=255):
    return max(minimum, min(maximum, value))


def blend(color1, color2, weight=0.5):
    return tuple(clamp(int(c1 * weight + c2 * (1 - weight))) for c1, c2 in zip(color1, color2))


def noise_pattern(width, height, base, variance=20, scale=0.35):
    data = []
    for y in range(height):
        for x in range(width):
            offset = int(math.sin((x + y) * scale) * variance) + int(math.cos((x - y) * scale) * variance)
            jitter = ((x * 13 + y * 7) & 0xFF) % (variance + 1) - variance // 2
            data.append((clamp(base[0] + offset + jitter), clamp(base[1] + offset + jitter), clamp(base[2] + offset + jitter), 255))
    return data


def save_texture(image, path):
    image.save(path, format='PNG')
    print(f"Saved {path}")


def generate_block(name, base, detail=None, detail_chance=0.12):
    image = Image.new('RGBA', (BLOCK_SIZE, BLOCK_SIZE))
    pixels = []
    for y in range(BLOCK_SIZE):
        for x in range(BLOCK_SIZE):
            if detail and (x + y * BLOCK_SIZE) % int(1 / detail_chance) == 0:
                pixels.append(detail + (255,))
            else:
                offset = (x * 7 ^ y * 13) % 16 - 8
                pixels.append((clamp(base[0] + offset), clamp(base[1] + offset), clamp(base[2] + offset), 255))
    image.putdata(pixels)
    return image


def grass_texture():
    image = Image.new('RGBA', (BLOCK_SIZE, BLOCK_SIZE))
    pixels = []
    for y in range(BLOCK_SIZE):
        for x in range(BLOCK_SIZE):
            t = y / BLOCK_SIZE
            top = (84, 153, 55)
            bottom = (98, 130, 58)
            color = blend(top, bottom, t)
            noise = ((x * 5 + y * 3) & 0x1F) - 16
            pixels.append((clamp(color[0] + noise), clamp(color[1] + noise), clamp(color[2] + noise), 255))
    image.putdata(pixels)
    return image


def dirt_texture():
    return generate_block('dirt', (109, 75, 45), (139, 90, 53), 0.1)


def stone_texture():
    return generate_block('stone', (123, 123, 123), (160, 160, 160), 0.08)


def cobblestone_texture():
    image = Image.new('RGBA', (BLOCK_SIZE, BLOCK_SIZE))
    draw = ImageDraw.Draw(image)
    stone = (95, 95, 95)
    highlight = (145, 145, 145)
    for y in range(0, BLOCK_SIZE, 8):
        for x in range(0, BLOCK_SIZE, 8):
            fill = highlight if (x + y) % 16 == 0 else stone
            draw.rectangle([x, y, x + 7, y + 7], fill=fill)
    return image


def wood_texture():
    image = Image.new('RGBA', (BLOCK_SIZE, BLOCK_SIZE))
    draw = ImageDraw.Draw(image)
    base = (121, 85, 58)
    for x in range(BLOCK_SIZE):
        stripe = int((x + (x % 4) * 2) * 1.5) % 32
        color = blend(base, (96, 60, 33), 0.3 if stripe < 16 else 0.6)
        for y in range(BLOCK_SIZE):
            draw.point((x, y), fill=color)
    return image


def planks_texture():
    image = Image.new('RGBA', (BLOCK_SIZE, BLOCK_SIZE))
    draw = ImageDraw.Draw(image)
    for y in range(BLOCK_SIZE):
        shade = 100 + (y % 4) * 8
        for x in range(BLOCK_SIZE):
            draw.point((x, y), fill=(150, shade, 100))
    return image


def leaves_texture():
    image = Image.new('RGBA', (BLOCK_SIZE, BLOCK_SIZE))
    pixels = []
    for y in range(BLOCK_SIZE):
        for x in range(BLOCK_SIZE):
            base = (81, 137, 72)
            noise = ((x * 17 + y * 11) & 0x1F) - 12
            shade = clamp(base[1] + noise)
            pixels.append((clamp(base[0] + noise), shade, clamp(base[2] + noise), 255))
    image.putdata(pixels)
    return image


def sand_texture():
    return generate_block('sand', (219, 210, 135), (237, 225, 151), 0.15)


def water_texture():
    image = Image.new('RGBA', (BLOCK_SIZE, BLOCK_SIZE))
    pixels = []
    for y in range(BLOCK_SIZE):
        for x in range(BLOCK_SIZE):
            base = (72, 129, 191)
            wave = int(math.sin((x + y) * 0.4) * 12)
            pixels.append((clamp(base[0] + wave), clamp(base[1] + wave), clamp(base[2] + wave + 15), 200))
    image.putdata(pixels)
    return image


def glass_texture():
    image = Image.new('RGBA', (BLOCK_SIZE, BLOCK_SIZE), (150, 190, 210, 130))
    draw = ImageDraw.Draw(image)
    for y in range(0, BLOCK_SIZE, 6):
        draw.line([(0, y), (BLOCK_SIZE, y)], fill=(200, 230, 240, 160))
        draw.line([(y, 0), (y, BLOCK_SIZE)], fill=(200, 230, 240, 160))
    return image


def brick_texture():
    image = Image.new('RGBA', (BLOCK_SIZE, BLOCK_SIZE))
    draw = ImageDraw.Draw(image)
    brick = (150, 60, 50)
    mortar = (130, 110, 90)
    for y in range(0, BLOCK_SIZE, 8):
        for x in range(0, BLOCK_SIZE, 8):
            if y // 8 % 2 == 1:
                offset = 4
            else:
                offset = 0
            draw.rectangle([x + offset, y, x + 7 + offset, y + 7], fill=brick)
    for y in range(0, BLOCK_SIZE, 8):
        draw.line([(0, y), (BLOCK_SIZE, y)], fill=mortar)
    for x in range(0, BLOCK_SIZE, 8):
        draw.line([(x, 0), (x, BLOCK_SIZE)], fill=mortar)
    return image


def ore_texture(base_color, speckle_color):
    image = generate_block('ore', base_color, None, 0.0)
    draw = ImageDraw.Draw(image)
    for _ in range(30):
        x = _ * 3 % BLOCK_SIZE
        y = (_ * 7 + 2) % BLOCK_SIZE
        draw.ellipse([x, y, x + 2, y + 2], fill=speckle_color)
    return image


def metallic_block(color):
    image = Image.new('RGBA', (BLOCK_SIZE, BLOCK_SIZE))
    pixels = []
    for y in range(BLOCK_SIZE):
        for x in range(BLOCK_SIZE):
            offset = int((x + y) * 0.5) % 8
            pixels.append((clamp(color[0] + offset), clamp(color[1] + offset), clamp(color[2] + offset), 255))
    image.putdata(pixels)
    return image


def obsidian_texture():
    return generate_block('obsidian', (25, 15, 80), (50, 35, 120), 0.06)


def bedrock_texture():
    return generate_block('bedrock', (45, 45, 50), (70, 70, 80), 0.08)


def ui_icon(name, color, accent=None):
    image = Image.new('RGBA', (UI_SIZE, UI_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    if name == 'crosshair':
        draw.line([(UI_SIZE/2, 6), (UI_SIZE/2, UI_SIZE-6)], fill=color, width=4)
        draw.line([(6, UI_SIZE/2), (UI_SIZE-6, UI_SIZE/2)], fill=color, width=4)
    elif name == 'hotbar':
        draw.rectangle([4, 4, UI_SIZE-4, UI_SIZE-4], outline=color, width=6)
    elif name == 'ammo':
        draw.rectangle([12, 24, UI_SIZE-12, UI_SIZE-20], fill=color)
        draw.ellipse([UI_SIZE/2-8, 16, UI_SIZE/2+8, 32], fill=accent or (255,255,255))
    elif name == 'heart':
        draw.polygon([(UI_SIZE*0.5, UI_SIZE*0.85), (UI_SIZE*0.1, UI_SIZE*0.4), (UI_SIZE*0.25, 6), (UI_SIZE*0.5, UI_SIZE*0.2), (UI_SIZE*0.75, 6), (UI_SIZE*0.9, UI_SIZE*0.4)], fill=color)
    elif name == 'button':
        draw.rounded_rectangle([8, 18, UI_SIZE-8, UI_SIZE-18], radius=12, outline=color, width=6, fill=(30, 30, 30, 220))
    return image


def create_textures():
    blocks = {
        'grass_block': grass_texture(),
        'dirt': dirt_texture(),
        'stone': stone_texture(),
        'cobblestone': cobblestone_texture(),
        'oak_log': wood_texture(),
        'oak_planks': planks_texture(),
        'oak_leaves': leaves_texture(),
        'sand': sand_texture(),
        'water': water_texture(),
        'glass': glass_texture(),
        'brick': brick_texture(),
        'gold_block': metallic_block((220, 190, 45)),
        'iron_block': metallic_block((190, 190, 190)),
        'diamond_block': metallic_block((95, 175, 210)),
        'coal_ore': ore_texture((80, 80, 80), (10, 10, 10)),
        'obsidian': obsidian_texture(),
        'bedrock': bedrock_texture(),
    }

    for name, image in blocks.items():
        save_texture(image, f'textures/blocks/{name}.png')

    ui = {
        'crosshair': ui_icon('crosshair', (255, 255, 255)),
        'hotbar': ui_icon('hotbar', (255, 255, 255)),
        'button': ui_icon('button', (255, 255, 255)),
        'heart': ui_icon('heart', (240, 60, 80)),
        'food': ui_icon('ammo', (255, 210, 80), accent=(240, 110, 20)),
        'inventory': ui_icon('button', (200, 200, 210)),
    }

    for name, image in ui.items():
        save_texture(image, f'textures/ui/{name}.png')


if __name__ == '__main__':
    create_textures()
