from PIL import Image, ImageDraw, ImageFilter, ImageFont
import os, math

# === 配置 ===
CANVAS_W = 1080
CANVAS_H = 1920

ASSETS_DIR = r"D:\项目\小白录制-应用商店宣传图\assets"
OUT_DIR = r"D:\项目\小白录制-应用商店宣传图"

files = [
    "theme-light.jpg",   # 浅色白蓝
    "theme-dark.jpg",    # 深色黑蓝
    "theme-green.jpg",   # 浅绿
    "theme-warm.jpg",    # 暖棕
    "theme-teal.jpg",    # 青蓝
]

PHONE_W = 730
CORNER_RADIUS = 44
ANGLES = [15, 7.5, 0, -7.5, -15]
BOTTOM_SPACING = 155
BOTTOM_Y = 1980
CENTER_X = CANVAS_W // 2

# === 1. 加载手机截图 ===
phones = []
for f in files:
    img = Image.open(os.path.join(ASSETS_DIR, f)).convert("RGBA")
    ratio = PHONE_W / img.width
    new_h = int(img.height * ratio)
    img = img.resize((PHONE_W, new_h), Image.LANCZOS)
    mask = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([(0, 0), (img.width - 1, img.height - 1)],
                        radius=CORNER_RADIUS, fill=255)
    img.putalpha(mask)
    phones.append(img)

# === 2. 奶油暖色渐变背景 ===
bg = Image.new("RGBA", (CANVAS_W, CANVAS_H), (255, 255, 255, 255))
top_color = (250, 248, 244, 255)
bot_color = (235, 230, 222, 255)
for y in range(CANVAS_H):
    t = y / CANVAS_H
    r = int(top_color[0] + (bot_color[0] - top_color[0]) * t)
    g = int(top_color[1] + (bot_color[1] - top_color[1]) * t)
    b = int(top_color[2] + (bot_color[2] - top_color[2]) * t)
    ImageDraw.Draw(bg).line([(0, y), (CANVAS_W, y)], fill=(r, g, b, 255))

# === 3. 标题 ===
draw = ImageDraw.Draw(bg)
title_font = ImageFont.truetype(r"C:\Windows\Fonts\msyhbd.ttc", 64)
title = "多主题·随心切换"
bbox = draw.textbbox((0, 0), title, font=title_font)
tw = bbox[2] - bbox[0]
th = bbox[3] - bbox[1]
draw.text(((CANVAS_W - tw) // 2, 160), title, fill=(50, 48, 45, 255), font=title_font)

# 标题下方装饰线
line_y = 160 + th + 20
draw.line([(CENTER_X - 60, line_y), (CENTER_X + 60, line_y)],
          fill=(180, 160, 130, 255), width=3)

# === 4. 逐张旋转并粘贴 ===
for i, (phone, angle) in enumerate(zip(phones, ANGLES)):
    w, h = phone.size

    margin_x = int(w * 0.7)
    temp_w = w + margin_x * 2
    temp_h = 2 * h + 120

    temp = Image.new("RGBA", (temp_w, temp_h), (0, 0, 0, 0))

    px = (temp_w - w) // 2
    py = temp_h // 2 - h
    temp.paste(phone, (px, py), phone)

    rotated = temp.rotate(angle, expand=False, resample=Image.BICUBIC)

    target_cx = CENTER_X + (i - 2) * BOTTOM_SPACING
    target_cy = BOTTOM_Y
    paste_x = int(target_cx - rotated.width // 2)
    paste_y = int(target_cy - rotated.height // 2)

    # 阴影
    shadow = Image.new("RGBA", rotated.size, (0, 0, 0, 0))
    alpha = rotated.split()[3]
    sdraw = ImageDraw.Draw(shadow)
    sdraw.bitmap((0, 0), alpha, fill=(0, 0, 0, 40))
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))

    bg.paste(shadow, (paste_x + 6, paste_y - 14), shadow)
    bg.paste(rotated, (paste_x, paste_y), rotated)

# === 5. 保存 ===
out_path = os.path.join(OUT_DIR, "多主题扇形展开宣传图.png")
bg.convert("RGB").save(out_path, "PNG", quality=95)
print(f"Saved: {out_path}")
print(f"Size: {bg.size}")
