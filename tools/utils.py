import os, math
from random import shuffle


def mkdir_if_none(path: str) -> str:
    """Create dir if none"""
    if not os.path.isdir(path):
        os.mkdir(path)
    return path


def create_arc(
    pos: tuple,
    *,
    direction: int,
    arc: float,
    distance: float,
    count: int,
    increment: int = 0,
):
    """Return coordinates along arc"""
    coords = []
    for i in range(count):
        a = direction - (arc / 2) + (i / (count - 1) * arc) if count > 1 else direction
        rad = a / 180 * math.pi
        d = distance + (i / count * increment)
        x = pos[0] + d * math.cos(rad)
        y = pos[1] + d * -math.sin(rad)
        coords.append((x, y, a - 90))
    return coords


def zindex_coords(coords: list[tuple]):
    """Reorder coords so center items are on top"""
    x = math.ceil(len(coords) / 2)
    half = coords[x:]
    half.reverse()
    return [*half, *coords[:x]]


def shuffle_tuple(val: tuple) -> tuple:
    """Shuffle a tuple in place"""
    n = list(val)
    shuffle(n)
    return tuple(n)


def shuffle_list(val: list) -> list:
    """Shuffle a list in place"""
    shuffle(val)
    return val


def flip_roll(col: tuple, flip: bool, shift: int) -> tuple:
    """Flip and roll a tuple in place"""
    col = list(col)
    if flip:
        col = list(reversed(col))
    return tuple(roll(col, shift))


def roll(arr: list, shift: int) -> list:
    shift %= len(arr)
    return [*arr[-shift:], *arr[:-shift]]
