from PIL import Image, ImageDraw, ImageFilter
from random import randint, choice
from tools.utils import create_arc
from tools.draw import create_gradient


def create_star(
    size: tuple[int, int],
    col1: list,
    col2: list,
    col3: list,
) -> Image.Image:
    """Create star sprite"""
    w, h = size
    h1 = int(h * 0.5)
    h2 = h - h1
    im = Image.new("RGBA", size)
    if h1:
        im.paste(create_gradient((w, h1), col3, col2))
    im.paste(create_gradient((w, h2), col2, col1), (0, h1))
    return im


def create_flash(
    size: tuple[int, int],
    thickness: int,
    fill: tuple,
    outline: tuple,
) -> Image.Image:
    """Create muzzle flash image"""
    w, h = size
    x = int(w / 2)
    im = Image.new("RGBA", size)
    draw = ImageDraw.Draw(im)

    n = randint(5, 15)
    coords = [(x, h - 1)]
    arc1 = create_arc((x, h - 1), direction=90, arc=60, distance=h, count=n)
    arc2 = create_arc((x, h - 1), direction=90, arc=60, distance=int(h * 0.75), count=n)
    for i, a in enumerate(arc1):
        px, py, pr = arc2[i] if (i % 2 == 1) else a
        py += int((abs(i - int(n / 2)) / int(n / 2)) * randint(int(h / 3), int(h / 2)))
        coords.append((px, py))

    draw.polygon(
        coords,
        fill=fill,
        outline=outline,
        width=thickness,
    )
    return im


def create_bullet(
    size: tuple[int, int],
    *,
    thickness: int,
    radius: int,
    fill: tuple,
    outline: tuple,
    type: str = None,
) -> Image.Image:
    """Create bullet sprite"""
    im = Image.new("RGBA", size)
    draw = ImageDraw.Draw(im)
    w, h = size
    if not type:
        type = choice(["arrow", "chevron", "diamond", "double", "square", "round"])

    match type:
        case "arrow":
            x = w / 2
            y = h / 4
            draw.polygon(
                ((0, h - 1), (x, h - y), (w - 1, h - 1), (x, 0)),
                fill=fill,
                outline=outline,
                width=int(thickness / 2),
            )
        case "chevron":
            x = w / 2
            y = h / 5
            draw.polygon(
                ((0, y), (x, 0), (w - 1, y), (w - 1, h - 1), (x, h - y), (0, h - 1)),
                fill=fill,
                outline=outline,
                width=thickness,
            )
        case "diamond":
            x = w / 2
            y = h / 4
            draw.polygon(
                ((0, y), (x, 0), (w - 1, y), (x, h - 1)),
                fill=fill,
                outline=outline,
                width=int(thickness / 2),
            )
        case "double":
            v = w / 3
            draw.rounded_rectangle(
                (0, 0, v, h - 1),
                fill=fill,
                outline=outline,
                width=int(thickness / 2),
                radius=radius,
            )
            draw.rounded_rectangle(
                (w - v - 1, 0, w - 1, h - 1),
                fill=fill,
                outline=outline,
                width=int(thickness / 2),
                radius=radius,
            )
        case "square":
            draw.rounded_rectangle(
                (0, 0, w - 1, h - 1),
                fill=fill,
                outline=outline,
                width=thickness,
                radius=radius,
            )
        case "round":
            draw.ellipse(
                (0, 0, w - 1, h - 1),
                fill=fill,
                outline=outline,
                width=thickness,
            )
    return im


def create_ship(
    size: tuple[int, int],
    *,
    body_color: tuple,
    pod_color: tuple,
    detail_color: tuple,
):
    """Create ship sprite"""
    width, height = size
    x_mid = int(width / 2)

    wing_base_height_min = int(height / 4)
    wing_base_top = randint(0, height - 1 - wing_base_height_min)
    wing_base_bottom = wing_base_top + randint(
        wing_base_height_min, height - 1 - wing_base_top
    )
    wing_tip_height_max = int((wing_base_bottom - wing_base_top) / 2)
    wing_tip_top = randint(0, height - 1 - wing_tip_height_max)
    wing_tip_bottom = wing_tip_top + randint(0, wing_tip_height_max)

    body_width_min = int(width / 15)
    body_width_max = int(width / 7)
    body_split_max = int(min(width, height) / 15)
    body_split_width = randint(0, body_split_max)
    body_top_width = randint(0, body_split_max)
    body_mid_width = randint(body_top_width, body_width_max)
    body_bottom_width = randint(0, body_width_min)
    body_mid_top = randint(body_top_width, height - 1 - body_bottom_width)

    split_top = randint(0, int(height / 2))
    split_bottom = randint(split_top + body_split_width, height - 1)

    pod_width = randint(
        max(body_split_width, body_split_max), body_split_width + body_split_max
    )
    pod_height = randint(pod_width * 2, int(height / 2))
    pod_top = randint(0, min(int(height / 2), height - pod_height))

    wing = [
        (x_mid + body_split_width, wing_base_top),
        (x_mid + body_split_width, wing_base_bottom),
        (width - 1, wing_tip_bottom),
        (width - 1, wing_tip_top),
    ]
    body = [
        (x_mid + body_split_width, 0),
        (x_mid + body_split_width + body_top_width, body_top_width),
        (x_mid + body_split_width + body_mid_width, body_mid_top),
        (x_mid + body_split_width + body_bottom_width, height - 1 - body_bottom_width),
        (x_mid + body_split_width, height - 1),
    ]
    split = [
        (x_mid, split_top),
        (x_mid + body_split_width, split_top),
        (x_mid + body_split_width, split_bottom),
        (x_mid, split_bottom),
    ]
    pod = [
        (x_mid, pod_top),
        (x_mid + pod_width, pod_top + pod_height / 2),
        (x_mid, pod_top + pod_height),
    ]

    im = Image.new("RGBA", size)
    draw = ImageDraw.Draw(im)
    draw.polygon(wing, fill=body_color)
    draw.polygon(split, fill=body_color)
    draw.polygon(body, fill=body_color)
    draw.line((*body[2], *body[3]), fill=detail_color, width=1)
    draw.line((*pod[1], *wing[1]), fill=detail_color, width=1)
    draw.line(
        (
            x_mid + body_split_width,
            (wing_base_top + wing_base_bottom) / 2,
            width - 1,
            wing_tip_top,
        ),
        fill=detail_color,
        width=1,
    )
    draw.polygon(pod, fill=pod_color)
    im.alpha_composite(im.transpose(Image.Transpose.FLIP_LEFT_RIGHT))

    return (
        im.filter(ImageFilter.SMOOTH)
        .filter(ImageFilter.SHARPEN)
        .filter(ImageFilter.SHARPEN)
    )


def create_powerup(
    *,
    size: tuple[int, int],
    sides: int,
    col1: tuple,
    col2: tuple,
):
    """Create powerup sprite"""
    width, height = size
    thickness = int(min(width, height) / 7)
    x = int(width / 2)
    y = int(height / 2)
    im = Image.new("RGBA", size)
    draw = ImageDraw.Draw(im)

    draw.regular_polygon(
        bounding_circle=(x, y, x - 1),
        n_sides=sides,
        fill=col2,
        outline=col2,
        width=thickness,
    )

    draw.regular_polygon(
        bounding_circle=(x, y, x - thickness - 1),
        n_sides=sides,
        fill=col1,
        outline=(127, 127, 127),
        width=int(thickness / 2),
    )

    return im.filter(ImageFilter.SMOOTH).filter(ImageFilter.SHARPEN)


def create_boom(
    size: tuple[int, int],
    *,
    col1: tuple,
    col2: tuple,
    col3: tuple,
    col4: tuple,
):
    """Create explosion sprite"""
    width, height = size
    thickness = int(min(width, height) / 20)
    pad = thickness * 2
    x = int(width / 2)
    y = int(height / 2)
    x2 = int(width / 8)
    y2 = int(height / 8)
    im = Image.new("RGBA", size, tuple([*list(col1), 0]))
    draw = ImageDraw.Draw(im)
    for i in range(5):
        draw.ellipse(
            (
                randint(pad, x),
                randint(pad, y),
                randint(x, width - 1 - pad),
                randint(y, height - 1 - pad),
            ),
            outline=col1,
            fill=col2,
            width=thickness,
        )
    for i in range(5):
        draw.ellipse(
            (
                randint(pad + x2, x),
                randint(pad + y2, y),
                randint(x, width - 1 - pad - x2),
                randint(y, height - 1 - pad - y2),
            ),
            outline=col3,
            fill=col4,
            width=thickness,
        )

    return (
        im.filter(ImageFilter.GaussianBlur(thickness))
        .convert("P", colors=32)
        .convert("RGBA")
    )
