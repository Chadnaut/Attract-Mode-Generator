from PIL import Image, ImageDraw, ImageFont
from tools.utils import zindex_coords, create_arc
import numpy as np


def create_gradient(size: tuple[int, int], col1: list, col2: list) -> Image.Image:
    """Return image containing gradient"""
    return Image.fromarray(
        np.tile(
            np.rot90([np.linspace(col2, col1, size[1], True, dtype=np.uint8)]),
            (size[0], 1),
        )
    )


def palettize(noise: np.ndarray, palette: np.ndarray):
    """Apply palette to array of indexes"""
    return Image.fromarray(palette[np.uint8((noise + 1) * 127.5)])


def draw_stock(
    img: Image.Image,
    *,
    ship: Image.Image,
    lives: int,
    pos: tuple[int, int],
    scale: float,
):
    """Draw remaining ships"""
    w = ship.width
    h = ship.height
    sw = int(w * scale)
    sh = int(h * scale)
    sm = int(sw * 0.5)
    stock = ship.resize((sw, sh))
    for n in range(lives):
        img.alpha_composite(stock, (pos[0] + (sw + sm) * n, img.height - sh - pos[1]))


def draw_score(
    img: Image.Image,
    *,
    font: ImageFont,
    pos: tuple[int, int],
    align: str,
    player: str,
    score: int,
):
    """Draw scores"""
    score_pad = f"{score}".rjust(8, "0")
    text = f"{player}\n{score_pad}"
    anchor = "ra" if align == "right" else "ma" if align == "center" else "la"
    ImageDraw.Draw(img).text(
        xy=(pos[0] + 1, pos[1] + 1),
        text=text,
        anchor=anchor,
        align=align,
        font=font,
        fill=(0, 0, 0),
    )
    ImageDraw.Draw(img).text(
        xy=pos,
        text=text,
        anchor=anchor,
        align=align,
        font=font,
        fill=(255, 255, 255),
    )


def draw_bullet_spread(
    img: Image.Image,
    *,
    pos: tuple,
    bullet: Image.Image,
    direction: int = 90,
    arc: float = 0,
    distance: float = 40,
    count: int = 1,
    start_dist: int = 40,
    rows: int = 1,
    alternate: bool = False,
    increment: bool = False,
):
    """Draw bullets in arc to image"""
    for r in range(rows):
        odd = r % 2
        alt = alternate and odd
        row_arc = row_arc = (arc / count * (count - 1)) if alt else arc
        c = count - 1 if alt else count
        d = start_dist + r * distance
        for x, y, a in zindex_coords(
            create_arc(
                pos,
                direction=direction,
                arc=row_arc,
                distance=d,
                count=c,
                increment=distance if increment else 0,
            )
        ):
            b = bullet.rotate(a, expand=True, resample=Image.Resampling.BILINEAR)
            img.alpha_composite(b, (int(x - b.width / 2), int(y - b.height / 2)))


def draw_item(img: Image.Image, *, item: Image.Image, pos: tuple[int, int]):
    """Draw item to img"""
    img.alpha_composite(
        item, (int(pos[0] - item.width / 2), int(pos[1] - item.height / 2))
    )


def draw_item_shadow(
    img: Image.Image,
    *,
    item: Image.Image,
    pos: tuple[int, int],
    shadow_color: tuple,
    shadow_pos: tuple[int, int],
    shadow_scale: float,
):
    """Draw item with shadow to img"""
    size = (int(item.width * shadow_scale), int(item.height * shadow_scale))
    shadow = Image.new("RGBA", size)
    shadow.paste(
        Image.new("RGBA", size, color=shadow_color),
        mask=item.getchannel("A").resize(size, resample=Image.Resampling.NEAREST),
    )
    draw_item(img, item=shadow, pos=(pos[0] + shadow_pos[0], pos[1] + shadow_pos[1]))
    draw_item(img, item=item, pos=pos)


def draw_gradient_text(
    img: Image.Image,
    *,
    text: str,
    font: ImageFont.FreeTypeFont,
    stroke: int,
    stroke_color: list,
    pad: list,
    stretch: bool = False,
    col1: list,
    col2: list,
):
    """Draw text with gradient to image"""

    # Get text bounding box
    txt_img = Image.new(mode="RGBA", size=(1, 1))
    txt_bbox = ImageDraw.Draw(txt_img).textbbox(
        xy=(0, 0),
        text=text,
        font=font,
        stroke_width=stroke,
    )

    # Find scale to fit text inside image
    iw = img.width
    ih = img.height
    space = 1 + stroke
    w = txt_bbox[2] - txt_bbox[0] + space * 2
    h = txt_bbox[3] - txt_bbox[1] + space * 2
    inner_w = iw - (pad[0] - space) * 2
    inner_h = ih - (pad[1] - space) * 2
    txt_xy = (-txt_bbox[0] + space, -txt_bbox[1] + space)

    if stretch:
        w2 = inner_w
        h2 = inner_h
    else:
        scale_x = inner_w / w
        scale_y = inner_h / h
        txt_ratio = w / h
        inner_ratio = inner_w / inner_h
        scale = scale_x if txt_ratio > inner_ratio else scale_y
        w2 = int(w * scale)
        h2 = int(h * scale)

    # Text fill
    txt_fill = Image.new(mode="L", size=(w, h))
    ImageDraw.Draw(txt_fill).text(
        xy=txt_xy,
        text=text,
        font=font,
        align="center",
        stroke_width=stroke,
        fill=(255),
        stroke_fill=(0),
    )

    # Text stroke
    txt_stroke = Image.new(mode="RGBA", size=(w, h), color=(0, 0, 0, 0))
    ImageDraw.Draw(txt_stroke).text(
        xy=txt_xy,
        text=text,
        font=font,
        align="center",
        stroke_width=stroke,
        fill=(0, 0, 0, 0),
        stroke_fill=tuple(stroke_color),
    )

    # Composite
    txt_img = Image.new(mode="RGB", size=(w, h))
    txt_img.paste(create_gradient((w, h), col1, col2))
    txt_img.putalpha(txt_fill)
    txt_img.alpha_composite(txt_stroke)
    txt_img = txt_img.resize((w2, h2))
    img.alpha_composite(txt_img, (int((iw - w2) / 2), int((ih - h2) / 2)))
