import os
from random import randint, choice, random
from PIL import Image, ImageFont

from tools.rand import Rand
from tools.utils import create_arc, shuffle_tuple, shuffle_list, flip_roll
from tools.sprite import (
    create_flash,
    create_bullet,
    create_ship,
    create_powerup,
    create_boom,
)
from tools.background import draw_landscape, draw_starfield
from tools.draw import (
    draw_stock,
    draw_score,
    draw_bullet_spread,
    draw_item,
    draw_item_shadow,
    draw_gradient_text,
)


def rand_tf() -> bool:
    return choice([True, False])


def rand_roll() -> int:
    return randint(0, 2)


def rand_light_color() -> list:
    return shuffle_list([255, choice([64, 128, 255]), choice([0, 64, 128])])


def rand_med_color() -> list:
    return shuffle_list([128, choice([0, 32, 64]), choice([0, 64, 128])])


def rand_dark_color() -> list:
    return shuffle_list([0, choice([0, 16, 32]), choice([0, 16, 32])])


def generate_snap(name: str, basic: bool, snaps_path: str, rand: Rand):
    w, h = rand.snap_size()
    img = Image.new(mode="RGBA", size=(w, h), color=(0, 0, 0, 255))

    v = min(w, h)
    v240 = int(v / 1)
    v120 = int(v / 2)
    v100 = int(v / 2.4)
    v80 = int(v / 3)
    v60 = int(v / 4)
    v48 = int(v / 5)
    v40 = int(v / 6)
    v30 = int(v / 8)
    v20 = int(v / 12)
    v16 = int(v / 16)
    v10 = int(v / 24)
    v8 = int(v / 30)
    v7 = int(v / 34)
    v5 = int(v / 48)
    v4 = int(v / 60)
    v2 = int(v / 120)
    v1 = int(v / 240)

    show_overlay = True
    show_ship = True
    show_wingman = random() < 0.2
    show_enemy = rand_tf()
    show_powerup = rand_tf()
    show_squad = rand_tf()
    show_boom1 = rand_tf()
    show_boom2 = rand_tf()
    show_starfield = True
    show_hyperspace = rand_tf()
    show_landscape = not basic
    show_space = rand_tf()

    boom_flip = rand_tf()
    boom_roll = rand_roll()
    boom_col1 = flip_roll((255, 0, 0), boom_flip, boom_roll)
    boom_col2 = flip_roll((255, 150, 0), boom_flip, boom_roll)
    boom_col3 = flip_roll((255, 255, 0), rand_tf(), rand_roll())
    boom_col4 = (255, 255, 255)

    ship_width = v30
    ship_height = v40
    wingman_width = v16
    wingman_height = v20

    shadow_color = (0, 0, 0, 0) if show_space else (0, 0, 0, 64)
    shadow_pos = (randint(-v10, v10), randint(v10, v20))
    shadow_scale = v10 / shadow_pos[1]

    ship_pos = (w * (0.1 + 0.8 * random()), h * (0.6 + 0.3 * random()))
    enemy_pos = (w * (0.2 + 0.6 * random()), h * (0.2 + 0.1 * random()))
    wingman_offset = (int(ship_width * 1), int(ship_height * 0.15))
    wingman_pos1 = (
        ship_pos[0] + wingman_offset[0],
        ship_pos[1] + wingman_offset[1],
    )
    wingman_pos2 = (
        ship_pos[0] - wingman_offset[0],
        ship_pos[1] + wingman_offset[1],
    )

    if show_starfield:
        draw_starfield(
            img,
            randint(150, 250),
            (v1, v1),
            [255, 255, 255, 128],
            [255, 255, 255, 128],
            [255, 255, 255, 128],
        )

    if show_hyperspace:
        s_hyper = random() < 0.1
        s_count = 300 if s_hyper else randint(30, 60)
        s_height = v240 if s_hyper else randint(v10, v30)
        draw_starfield(
            img,
            s_count,
            (v1, s_height),
            [*flip_roll((100, 100, 200), rand_tf(), rand_roll()), 128],
            [*flip_roll((100, 0, 200), rand_tf(), rand_roll()), 128],
            [*flip_roll((200, 0, 200), rand_tf(), rand_roll()), 0],
        )

    if show_landscape:
        draw_landscape(img, show_space)

    if show_enemy:
        e_flip = rand_tf()
        e_roll = rand_roll()
        enemy = create_ship(
            size=(v80, v60),
            body_color=flip_roll((30, 45, 30), e_flip, e_roll),
            pod_color=(220, 0, 0),
            detail_color=flip_roll((60, 80, 60), e_flip, e_roll),
        ).rotate(180, expand=True)
        draw_item_shadow(
            img,
            item=enemy,
            pos=enemy_pos,
            shadow_color=shadow_color,
            shadow_pos=shadow_pos,
            shadow_scale=shadow_scale,
        )

    show_squad = True
    if show_squad:
        squad = create_ship(
            size=(v16, v20),
            body_color=shuffle_tuple((255, 90, 90)),
            pod_color=(220, 0, 0),
            detail_color=(90, 90, 90),
        )
        squad_coords = create_arc(
            pos=(w * (0.4 + 0.2 * random()), h * (0.4 + 0.2 * random())),
            direction=randint(0, 360),
            arc=randint(50, 90),
            distance=randint(v80, v120),
            count=randint(1, 4),
        )
        for coord in squad_coords:
            draw_item_shadow(
                img,
                item=squad.rotate(
                    coord[2] - 90,
                    expand=True,
                    resample=Image.Resampling.BILINEAR,
                ),
                pos=(coord[0], coord[1]),
                shadow_color=shadow_color,
                shadow_pos=shadow_pos,
                shadow_scale=shadow_scale,
            )

    if show_powerup:
        powerup = create_powerup(
            size=(v20, v20),
            sides=randint(3, 8),
            col1=shuffle_tuple((0, 220, choice([220, 0]))),
            col2=(220, 220, 220),
        )
        draw_item_shadow(
            img,
            item=powerup,
            pos=(w * (0.1 + 0.8 * random()), h * (0.2 + 0.6 * random())),
            shadow_color=shadow_color,
            shadow_pos=shadow_pos,
            shadow_scale=shadow_scale,
        )

    if show_ship:
        ship_beam = random() < 0.05
        ship_bullet_rows = randint(0, 5)
        ship_bullet_arc = randint(0, 15)
        ship_bullet_count = randint(1, 5)
        ship_bullet_distance = randint(v30, v48)
        ship_bullet_start_dist = randint(v40, v100)
        ship_bullet_fill = (255, 255, 255)
        ship_bullet_outline = shuffle_tuple((0, 200, 255))

        ship = create_ship(
            size=(ship_width, ship_height),
            body_color=(220, 220, 220),
            pod_color=(0, 220, 220),
            detail_color=(200, 200, 200),
        )
        draw_item_shadow(
            img,
            item=ship,
            pos=ship_pos,
            shadow_color=shadow_color,
            shadow_pos=shadow_pos,
            shadow_scale=shadow_scale,
        )

        if show_wingman:
            wingman = create_ship(
                size=(wingman_width, wingman_height),
                body_color=(220, 220, 220),
                pod_color=(0, 220, 220),
                detail_color=(200, 200, 200),
            )
            draw_item_shadow(
                img,
                item=wingman,
                pos=wingman_pos1,
                shadow_color=shadow_color,
                shadow_pos=shadow_pos,
                shadow_scale=shadow_scale,
            )
            draw_item_shadow(
                img,
                item=wingman,
                pos=wingman_pos2,
                shadow_color=shadow_color,
                shadow_pos=shadow_pos,
                shadow_scale=shadow_scale,
            )

    if show_boom1:
        boom_size1 = randint(v60, v100)
        boom1 = create_boom(
            size=(boom_size1, boom_size1),
            col1=boom_col1,
            col2=boom_col2,
            col3=boom_col3,
            col4=boom_col4,
        )
        draw_item(
            img,
            item=boom1,
            pos=(w * (0.1 + 0.8 * random()), h * (0.1 + 0.8 * random())),
        )

    if show_boom2:
        boom_size2 = randint(v30, v60)
        boom2 = create_boom(
            size=(boom_size2, boom_size2),
            col1=boom_col1,
            col2=boom_col2,
            col3=boom_col3,
            col4=boom_col4,
        )
        draw_item(
            img,
            item=boom2,
            pos=(w * (0.1 + 0.8 * random()), h * (0.1 + 0.8 * random())),
        )

    if show_ship:
        if ship_beam:
            ship_bullet = create_bullet(
                size=(randint(v20, v30), h),
                thickness=v2,
                radius=v30,
                fill=ship_bullet_fill,
                outline=ship_bullet_outline,
                type="square",
            )
            draw_bullet_spread(
                img,
                pos=ship_pos,
                bullet=ship_bullet,
                distance=0,
                count=1,
                start_dist=(h + ship_height) / 2,
                rows=1,
            )
            if show_wingman:
                ship_bullet = create_bullet(
                    size=(randint(v5, v10), h),
                    thickness=v2,
                    radius=v10,
                    fill=ship_bullet_fill,
                    outline=ship_bullet_outline,
                    type="square",
                )
                draw_bullet_spread(
                    img,
                    pos=wingman_pos1,
                    bullet=ship_bullet,
                    distance=0,
                    count=1,
                    start_dist=(h + wingman_height) / 2,
                    rows=1,
                )
                draw_bullet_spread(
                    img,
                    pos=wingman_pos2,
                    bullet=ship_bullet,
                    distance=0,
                    count=1,
                    start_dist=(h + wingman_height) / 2,
                    rows=1,
                )
        else:
            ship_bullet = create_bullet(
                size=(randint(v8, v10), v20),
                thickness=v2,
                radius=v4,
                fill=ship_bullet_fill,
                outline=ship_bullet_outline,
            )
            draw_bullet_spread(
                img,
                pos=ship_pos,
                bullet=ship_bullet,
                arc=ship_bullet_arc,
                distance=ship_bullet_distance,
                count=ship_bullet_count,
                start_dist=ship_bullet_start_dist,
                rows=ship_bullet_rows,
            )
            if show_wingman:
                draw_bullet_spread(
                    img,
                    pos=(
                        wingman_pos1[0],
                        wingman_pos1[1] + (ship_height - wingman_height) / 2,
                    ),
                    bullet=ship_bullet,
                    arc=ship_bullet_arc,
                    distance=ship_bullet_distance,
                    count=1,
                    start_dist=ship_bullet_start_dist,
                    rows=ship_bullet_rows,
                )
                draw_bullet_spread(
                    img,
                    pos=(
                        wingman_pos2[0],
                        wingman_pos2[1] + (ship_height - wingman_height) / 2,
                    ),
                    bullet=ship_bullet,
                    arc=ship_bullet_arc,
                    distance=ship_bullet_distance,
                    count=1,
                    start_dist=ship_bullet_start_dist,
                    rows=ship_bullet_rows,
                )

            if ship_bullet_rows and (ship_bullet_start_dist < v60):
                ship_flash = create_flash(
                    size=(v30, v30),
                    thickness=v2,
                    fill=ship_bullet_fill,
                    outline=ship_bullet_outline,
                )
                draw_item(
                    img,
                    item=ship_flash,
                    pos=(
                        ship_pos[0],
                        ship_pos[1] - (ship_flash.height + ship_height) / 2,
                    ),
                )
                if show_wingman:
                    draw_item(
                        img,
                        item=ship_flash,
                        pos=(
                            wingman_pos1[0],
                            wingman_pos1[1] - (ship_flash.height + wingman_height) / 2,
                        ),
                    )
                    draw_item(
                        img,
                        item=ship_flash,
                        pos=(
                            wingman_pos2[0],
                            wingman_pos2[1] - (ship_flash.height + wingman_height) / 2,
                        ),
                    )

    if show_enemy:
        bullet_flip = rand_tf()
        bullet_roll = rand_roll()
        enemy_bullet = create_bullet(
            size=(randint(v8, v10), randint(v8, v40)),
            thickness=v2,
            radius=v4,
            fill=flip_roll((255, choice([255, 220]), 220), bullet_flip, bullet_roll),
            outline=flip_roll((255, 0, 0), bullet_flip, bullet_roll),
        )
        if random() < 0.3:
            # spiral
            draw_bullet_spread(
                img,
                pos=enemy_pos,
                bullet=enemy_bullet,
                direction=randint(0, 360),
                arc=360,
                distance=randint(v40, v48),
                count=36,
                start_dist=randint(v48, v100),
                rows=randint(0, 4),
                increment=True,
            )
        else:
            # spread
            draw_bullet_spread(
                img,
                pos=enemy_pos,
                bullet=enemy_bullet,
                direction=randint(250, 290),
                arc=randint(70, 90),
                distance=randint(v40, v48),
                count=randint(5, 9),
                start_dist=randint(v48, v100),
                rows=randint(0, 4),
                alternate=rand_tf(),
            )

    if show_overlay:
        score1 = randint(0, 99999)
        score2 = randint(0, 99999)
        highscore = max(score1, score2, randint(0, 99999))
        font = ImageFont.truetype(font=rand.font_display(), size=v7)
        draw_stock(
            img,
            ship=ship,
            lives=randint(1, 4),
            pos=(v5, v5),
            scale=0.25,
        )
        draw_score(
            img,
            pos=(v5, v5),
            font=font,
            align="left",
            player="PLAYER1",
            score=score1,
        )
        draw_score(
            img,
            pos=(w / 2, v5),
            font=font,
            align="center",
            player="HIGHSCORE",
            score=highscore,
        )
        draw_score(
            img,
            pos=(w - v5, v5),
            font=font,
            align="right",
            player="PLAYER2",
            score=score2,
        )

    img.convert("RGB").save(os.path.join(snaps_path, f"{name}.png"))


def generate_wheel(name: str, title: str, snaps_path: str, rand: Rand):
    size = rand.wheel_size()
    img = Image.new(mode="RGBA", size=size)

    # remove content in brackets
    text = title.split("(")[0].strip(" ")
    text_bg = ""

    # only line break if more than two words
    parts = text.split(" ")
    if len(parts) > 2:
        # last word short enough to place in background
        if len(parts[-1]) <= 5:
            text_bg = parts.pop().upper()
        # content long enough the break
        if len(" ".join(parts)) > 12:
            parts[randint(0, len(parts) - 1)] += "\n"
        text = (" ".join(parts)).replace("\n ", "\n")

    # common stroke for all words
    stroke = randint(2, 10)
    stroke_color = rand_dark_color()
    pad = [int(img.height / 20), int(img.height / 20)]

    if text_bg:
        # text as bg
        draw_gradient_text(
            img=img,
            text=text_bg,
            font=ImageFont.truetype(font=rand.font_foreground(), size=200),
            stroke=stroke,
            stroke_color=stroke_color,
            pad=pad,
            col1=rand_med_color(),
            col2=rand_med_color(),
            stretch=len(text_bg) > 3,
        )
        pad[1] = int(img.height / 4)
    elif random() > 0.6:
        # special font as bg
        draw_gradient_text(
            img=img,
            text=rand.fonts_background_char(),
            font=ImageFont.truetype(font=rand.font_background(), size=200),
            stroke=stroke,
            stroke_color=stroke_color,
            pad=pad,
            col1=rand_med_color(),
            col2=rand_med_color(),
        )

    # foreground text
    draw_gradient_text(
        img=img,
        text=text,
        font=ImageFont.truetype(font=rand.font_foreground(), size=100),
        stroke=stroke,
        stroke_color=stroke_color,
        pad=pad,
        col1=rand_light_color(),
        col2=rand_light_color(),
    )

    img.save(os.path.join(snaps_path, f"{name}.png"))
