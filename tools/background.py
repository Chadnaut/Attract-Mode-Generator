import numpy as np
from PIL import Image
from random import randint, choice, random
from pyfastnoiselite.pyfastnoiselite import FastNoiseLite, NoiseType, FractalType
from tools.utils import shuffle_list, roll
from tools.sprite import create_star
from tools.draw import palettize


def draw_starfield(
    img: Image.Image,
    count: int,
    size: tuple[int, int],
    col1: list,
    col2: list,
    col3: list,
):
    """Draw random stars"""
    height = size[1]
    star = np.array(create_star(size, col1, col2, col3))
    for i in range(count):
        x = randint(0, img.width)
        y = randint(-height, img.height)
        sa = star.copy()
        sa[..., 3] = random() * sa[..., 3]  # Random alpha
        s = Image.fromarray(sa)
        img.alpha_composite(s, (x, y))


def draw_landscape(img: Image.Image, show_space: bool = False):
    """Draw noise based landscape / nebula"""
    size = (img.width, img.height)

    # noise coarse
    ngen1 = FastNoiseLite(0)
    ngen1.noise_type = choice(
        [
            NoiseType.NoiseType_OpenSimplex2,
            NoiseType.NoiseType_OpenSimplex2S,
            NoiseType.NoiseType_Perlin,
            NoiseType.NoiseType_ValueCubic,
            NoiseType.NoiseType_Value,
            NoiseType.NoiseType_Cellular,
        ]
    )
    ngen1.fractal_type = choice(
        [
            FractalType.FractalType_FBm,
            FractalType.FractalType_PingPong,
        ]
    )
    is_cellular = ngen1.noise_type == NoiseType.NoiseType_Cellular
    freq = randint(4, 16) if is_cellular else max(0.1, random())
    ngen1.fractal_octaves = randint(1, 16)
    ngen1.frequency = freq / min(*size)

    # noise fine
    ngen2 = FastNoiseLite(0)
    ngen2.noise_type = ngen1.noise_type
    ngen2.fractal_type = ngen1.fractal_type
    ngen2.fractal_octaves = ngen1.fractal_octaves
    ngen2.frequency = ngen1.frequency * 4

    v0 = 0
    v1 = 80
    v2 = 150
    v3 = 180
    v4 = 200

    c1 = [0, 0, 0, 0]
    c2 = [0, 0, 0, 0]
    c3 = [0, 0, 0, 0]
    c4 = [0, 0, 0, 0]
    c5 = [0, 0, 0, 0]
    c6 = [0, 0, 0, 0]
    b2 = [0, 0, 0]
    b6 = [0, 0, 0]
    b2a = [0, 0, 0, 0, 0, 0]
    b6a = [0, 0, 0, 0, 0]

    if show_space:
        # space colours
        space_mode = choice([0, 0, 1, 2, 2])
        if space_mode == 0:
            if choice([True, False]):
                c1 = [v4, v4, v4, 255]  # cloud
                c2 = [*shuffle_list([v4, choice([v0, v4]), v0]), 0]
            if choice([True, False]):
                b2 = shuffle_list([v4, choice([v0, v4]), v0])  # cloud overlay
                b2a = [0, 64, 0, 48, 0, 0]
        elif space_mode == 1:
            c3 = [*shuffle_list([v4, choice([v0, v4]), v0]), 128]  # edges
            c4 = [*shuffle_list([v4, choice([v0, v4]), v0]), 128]
        else:
            if choice([True, False]):
                c5 = [*shuffle_list([v2, v0, v4]), 128]  # nebula
                c6 = [*shuffle_list([v4, choice([v0, v4]), v0]), 0]
            if choice([True, False]):
                b6 = shuffle_list([v4, choice([v0, v4]), v0])  # nebula overlay
                b6a = [0, 120, 160, 220, 255]
    else:
        # land colours
        inv1 = choice([True, False])
        inv2 = choice([True, False])
        inv3 = choice([True, False])
        roll1 = randint(0, 2)
        roll2 = randint(0, 2)
        roll3 = randint(0, 2)

        c1 = [*roll([v0, v0, v1] if not inv1 else [v1, v1, v0], roll1), 255]
        c2 = [*roll([v0, v0, v4] if not inv1 else [v4, v4, v0], roll1), 255]
        c3 = [*roll([v4, v3, v0] if not inv2 else [v0, v3, v4], roll2), 255]
        c4 = [*roll([v4, v2, v0] if not inv2 else [v0, v2, v4], roll2), 255]
        c5 = [*roll([v0, v2, v0] if not inv3 else [v2, v0, v2], roll3), 255]
        c6 = [*roll([v0, v1, v0] if not inv3 else [v1, v0, v1], roll3), 255]

        b2 = roll([v0, v4, v4] if not inv1 else [v4, v0, v0], roll1)
        b6 = roll([v0, v4, v0] if not inv3 else [v4, v0, v4], roll3)
        b2a = [0, 64, 0, 48, 0, 0]
        b6a = [0, 120, 160, 220, 255]

    # sea and land
    backg_palette = np.concatenate(
        (
            np.linspace(c1, c2, 128, False),
            np.linspace(c2, c3, 3, False),
            np.linspace(c3, c4, 10, False),
            np.linspace(c4, c5, 3, False),
            np.linspace(c5, c6, 30, False),
            np.linspace(c6, c5, 82, False),
        ),
        casting="unsafe",
        dtype=np.uint8,
    )

    # trees
    inner_palette = np.concatenate(
        (
            np.linspace([*b6, b6a[0]], [*b6, b6a[0]], 100, False),
            np.linspace([*b6, b6a[0]], [*b6, b6a[1]], 33, False),
            np.linspace([*b6, b6a[1]], [*b6, b6a[2]], 20, False),
            np.linspace([*b6, b6a[2]], [*b6, b6a[3]], 33, False),
            np.linspace([*b6, b6a[3]], [*b6, b6a[4]], 70, False),
        ),
        casting="unsafe",
        dtype=np.uint8,
    )

    # waves
    outer_palette = np.concatenate(
        (
            np.linspace([*b2, b2a[0]], [*b2, b2a[0]], 50, False),
            np.linspace([*b2, b2a[0]], [*b2, b2a[1]], 78, False),
            np.linspace([*b2, b2a[1]], [*b2, b2a[2]], 28, False),
            np.linspace([*b2, b2a[2]], [*b2, b2a[3]], 25, False),
            np.linspace([*b2, b2a[3]], [*b2, b2a[4]], 25, False),
            np.linspace([*b2, b2a[4]], [*b2, b2a[5]], 50, False),
        ),
        casting="unsafe",
        dtype=np.uint8,
    )

    # generate noise
    rx = np.linspace(0, size[0], size[0]) + randint(-1048576, 1048576)
    ry = np.linspace(0, size[1], size[1]) + randint(-1048576, 1048576)
    backg_noise = np.array([[ngen1.get_noise(x, y) for x in rx] for y in ry])
    detail_noise = np.array([[ngen2.get_noise(x, y) for x in rx] for y in ry])
    n3 = detail_noise + 1
    n4 = (backg_noise - 0.1) * 10
    inner_noise = n3 * np.clip(n4, 0, 1) - 1
    outer_noise = n3 * np.clip(-n4, 0, 1) - 1

    img.alpha_composite(palettize(backg_noise, backg_palette))
    img.alpha_composite(palettize(inner_noise, inner_palette))
    img.alpha_composite(palettize(outer_noise, outer_palette))
