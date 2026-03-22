import math
import random
import hashlib
import tempfile
from config import EMOTIONS, EMOTION_COLORS, PALETTES


_recent_combos = []

def pick_traits() -> dict:
    global _recent_combos
    palette_names = list(PALETTES.keys())

    # Try up to 20 times to get a unique emotion+palette combo
    for _ in range(20):
        emotion = random.choice(EMOTIONS)
        palette_name = random.choice(palette_names)
        combo = (emotion, palette_name)
        if combo not in _recent_combos:
            break

    # Track last 30 combos to avoid repeats
    _recent_combos.append(combo)
    if len(_recent_combos) > 30:
        _recent_combos = _recent_combos[-30:]

    # Add hue jitter so even same palette looks different
    base_hex = PALETTES[palette_name]["hex"]
    r = int(base_hex[1:3], 16)
    g = int(base_hex[3:5], 16)
    b = int(base_hex[5:7], 16)
    jitter = random.randint(-25, 25)
    r = max(0, min(255, r + jitter))
    g = max(0, min(255, g + random.randint(-15, 15)))
    b = max(0, min(255, b + random.randint(-15, 15)))
    palette_hex = f"#{r:02x}{g:02x}{b:02x}"

    seed = random.randint(0, 2**32)
    return {
        "emotion": emotion,
        "palette_name": palette_name,
        "palette_hex": palette_hex,
        "seed": seed,
    }


def generate(emotion: str, palette_hex: str, seed: int = 0) -> str:
    from PIL import Image, ImageDraw, ImageFilter

    r0 = int(palette_hex[1:3], 16)
    g0 = int(palette_hex[3:5], 16)
    b0 = int(palette_hex[5:7], 16)

    emotion_hex = EMOTION_COLORS.get(emotion, "#888888")
    er = int(emotion_hex[1:3], 16)
    eg = int(emotion_hex[3:5], 16)
    eb = int(emotion_hex[5:7], 16)

    rng_state = seed or random.randint(0, 2**32)

    def rng(n=1000):
        nonlocal rng_state
        rng_state = (rng_state * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
        return (rng_state >> 33) % n

    SIZE = 1024
    img = Image.new("RGB", (SIZE, SIZE), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background gradient — palette-driven
    for y in range(SIZE):
        t = y / SIZE
        cr = int(r0 * t * 0.25)
        cg = int(g0 * t * 0.25)
        cb = int(b0 * t * 0.25)
        draw.line([(0, y), (SIZE, y)], fill=(cr, cg, cb))

    cx, cy = SIZE // 2, SIZE // 2

    # Emotion-driven composition
    if emotion == "happy":
        # Bright radial burst
        for i in range(50 + rng(30)):
            angle = (i / 80) * 2 * math.pi + rng(100) / 100
            length = 200 + rng(300)
            ex = int(cx + math.cos(angle) * length)
            ey = int(cy + math.sin(angle) * length)
            draw.line([(cx, cy), (ex, ey)], fill=(min(255, r0 + 80), min(255, g0 + 80), min(255, b0 + 80)), width=1)

    elif emotion == "sad":
        # Downward curves
        for i in range(8 + rng(6)):
            rad = 80 + i * (50 + rng(20))
            offset = rng(100) + 50
            draw.arc([(cx - rad, cy - rad + offset), (cx + rad, cy + rad + offset)],
                     start=200 + rng(40), end=340 + rng(40),
                     fill=(r0 // 2, g0 // 2, b0 // 2), width=1 + rng(2))

    elif emotion == "anger":
        # Sharp angular lines
        for _ in range(30 + rng(20)):
            x1, y1 = rng(SIZE), rng(SIZE)
            x2, y2 = x1 + rng(200) - 100, y1 + rng(200) - 100
            draw.line([(x1, y1), (x2, y2)],
                      fill=(min(255, er + rng(60)), eg // 3, eb // 3), width=1 + rng(3))

    elif emotion == "love":
        # Warm overlapping ellipses
        for _ in range(12 + rng(8)):
            x, y = cx + rng(300) - 150, cy + rng(300) - 150
            rx, ry = 40 + rng(80), 40 + rng(80)
            draw.ellipse([(x - rx, y - ry), (x + rx, y + ry)],
                         outline=(min(255, er + rng(40)), eg // 2 + rng(40), eb // 2 + rng(40)),
                         width=1 + rng(2))

    elif emotion == "lust":
        # Dense particles, tight glow
        for _ in range(80 + rng(60)):
            dx = cx + rng(400) - 200
            dy = cy + rng(400) - 200
            dr = 2 + rng(8)
            draw.ellipse([(dx - dr, dy - dr), (dx + dr, dy + dr)],
                         fill=(min(255, er + rng(60)), eg // 2, min(255, eb + rng(60))))

    # Concentric rings (all emotions)
    for i in range(4 + rng(4)):
        rad = 50 + i * (45 + rng(25))
        draw.ellipse([(cx - rad, cy - rad), (cx + rad, cy + rad)],
                     outline=(min(255, r0 // 2 + rng(40)), min(255, g0 // 2 + rng(40)), min(255, b0 // 2 + rng(40))),
                     width=1)

    # Center glow
    for radius in range(60, 0, -3):
        t = radius / 60
        glow = (int(r0 * (1 - t) + er * t * 0.5),
                int(g0 * (1 - t) + eg * t * 0.5),
                int(b0 * (1 - t) + eb * t * 0.5))
        draw.ellipse([(cx - radius, cy - radius), (cx + radius, cy + radius)], fill=glow)

    # Blur
    try:
        img = img.filter(ImageFilter.GaussianBlur(radius=1.5))
    except Exception:
        pass

    # Save
    tmp = tempfile.NamedTemporaryFile(suffix=f"_{emotion}_{palette_hex.replace('#','')}.png", delete=False)
    img.save(tmp.name, "PNG")
    tmp.close()
    return tmp.name
