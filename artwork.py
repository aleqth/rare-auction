import tempfile


def generate_canvas(bg_color: str) -> str:
    """Generate a blank 768x987 canvas with background color and 3 dark slot outlines."""
    from PIL import Image, ImageDraw

    W, H = 768, 987
    img = Image.new("RGB", (W, H), bg_color)
    draw = ImageDraw.Draw(img)

    # Draw 3 faint slot rectangles
    slot_w = int(W * 0.121)
    slot_h = int(H * 0.083)
    slot_x = int(W * 0.439)
    for top_pct in [0.193, 0.330, 0.483]:
        slot_y = int(H * top_pct)
        draw.rectangle(
            [(slot_x, slot_y), (slot_x + slot_w, slot_y + slot_h)],
            fill=None,
            outline="#ffffff08",
            width=1,
        )

    tmp = tempfile.NamedTemporaryFile(suffix="_canvas.png", delete=False)
    img.save(tmp.name, "PNG")
    tmp.close()
    return tmp.name


def generate_composed(bg_color: str, slots: dict) -> str:
    """Generate the final composed artwork with background + colored slots."""
    from PIL import Image, ImageDraw

    W, H = 768, 987
    img = Image.new("RGB", (W, H), bg_color)
    draw = ImageDraw.Draw(img)

    slot_w = int(W * 0.121)
    slot_h = int(H * 0.083)
    slot_x = int(W * 0.439)
    tops = {1: 0.193, 2: 0.330, 3: 0.483}

    for slot_num, top_pct in tops.items():
        color = slots.get(str(slot_num)) or slots.get(slot_num)
        slot_y = int(H * top_pct)
        if color:
            draw.rectangle(
                [(slot_x, slot_y), (slot_x + slot_w, slot_y + slot_h)],
                fill=color,
            )
        else:
            draw.rectangle(
                [(slot_x, slot_y), (slot_x + slot_w, slot_y + slot_h)],
                fill=None,
                outline="#ffffff10",
                width=1,
            )

    tmp = tempfile.NamedTemporaryFile(suffix="_composed.png", delete=False)
    img.save(tmp.name, "PNG")
    tmp.close()
    return tmp.name
