import string, re, json, os, zipfile
from random import randint, choice, random, shuffle


def chance(percent: float) -> bool:
    return random() <= percent


def plural(value: str, keep: bool) -> str:
    return re.sub(r"\(([^)]+)\)", lambda m: m[1] if keep else "", value)


def trim(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


class Rand:
    data: dict
    fonts_display: list
    fonts_foreground: list
    fonts_background: list

    def __init__(self, path: str):
        with open(path) as file:
            self.data = json.load(file)
        self.__init_fonts()

    def __init_fonts(self):
        self.fonts_display = self.__get_path_fonts(self.data["font"]["display"])
        self.fonts_foreground = self.__get_path_fonts(self.data["font"]["foreground"])
        self.fonts_background = self.__get_path_fonts(self.data["font"]["background"])

    def __get_path_fonts(self, path: str):
        names = [f for f in next(os.walk(path), ([], [], []))[2] if f.endswith(".zip")]
        files = []
        for n in names:
            name = os.path.join(path, n)
            zip = zipfile.ZipFile(name)
            info = self.__get_best_font(zip)
            files.append((name, info))
        return files

    def __get_best_font(self, font_zip: zipfile.ZipFile) -> zipfile.ZipInfo:
        best = None
        file = None
        for info in font_zip.infolist():
            filename = info.filename
            if filename.lower().endswith(".ttf") or filename.lower().endswith(".otf"):
                if not best or len(filename) < len(best):
                    best = filename
                    file = info
        return file

    # Fonts return a file from zipped font - must open each time as it gets closed after use
    def font_foreground(self):
        font = choice(self.fonts_foreground)
        return zipfile.ZipFile(font[0]).open(font[1], "r")

    def font_display(self):
        font = choice(self.fonts_display)
        return zipfile.ZipFile(font[0]).open(font[1], "r")

    def font_background(self):
        font = choice(self.fonts_background)
        return zipfile.ZipFile(font[0]).open(font[1], "r")

    # Special case - bg font contains art for a limited number of characters
    def fonts_background_char(self):
        return choice(self.data["font"]["background_chars"])

    def snap_size(self) -> tuple[int, int]:
        return (
            randint(self.data["snap"]["width_min"], self.data["snap"]["width_max"]),
            randint(self.data["snap"]["height_min"], self.data["snap"]["height_max"]),
        )

    def wheel_size(self) -> tuple[int, int]:
        return (
            randint(self.data["wheel"]["width_min"], self.data["wheel"]["width_max"]),
            randint(self.data["wheel"]["height_min"], self.data["wheel"]["height_max"]),
        )

    def title(self) -> str:
        n = [True, True, chance(0.6)]
        shuffle(n)
        a = choice(self.data["title"]["first"]) if n[0] else ""
        b = choice(self.data["title"]["middle"]) if n[1] else ""
        c = plural(choice(self.data["title"]["last"]), chance(0.5)) if n[2] else ""
        d = choice(self.data["title"]["sequel"]) if chance(0.25) else ""
        e = choice(self.data["title"]["version"]) if chance(0.5) else ""
        return trim(f"{a} {b} {c} {d} {e}")

    def manufacturer(self) -> str:
        a = choice(self.data["manufacturer"]["head"])
        b = choice(self.data["manufacturer"]["tail"])
        c = choice(self.data["manufacturer"]["location"]) if chance(0.25) else ""
        d = f" / {self.manufacturer()}" if chance(0.125) else ""
        return trim(f"{a}{b} {c}{d}")

    def category(self) -> str:
        a = choice(self.data["category"]["type"])
        b = choice(self.data["category"]["subtype"])
        c = choice(self.data["category"]["orientation"]) if chance(0.25) else ""
        return trim(f"{a} / {b} {c}")

    def status(self) -> str:
        return choice(self.data["status"])

    def language(self) -> str:
        return choice(self.data["language"])

    def tags(self, limit) -> list[str]:
        tags = self.data["tags"]
        shuffle(tags)
        tags = tags[:limit]
        tags.sort()
        return tags

    def year(self) -> str:
        return choice(self.data["year"])

    def rotation(self) -> str:
        return choice(self.data["rotation"])

    def joystick(self) -> str:
        return choice(self.data["joystick"])

    def buttons(self) -> str:
        return choice(self.data["buttons"])

    def players(self) -> int:
        return choice(self.data["players"])

    def system(self) -> str:
        a = choice(self.data["system"]["head"])
        b = choice(self.data["system"]["tail"])
        c = choice(self.data["system"]["version"]) if chance(0.25) else ""
        return trim(f"{a}{b} {c}")

    def rule_str(self) -> str:
        field = choice(["Title", "Manufacturer"])
        compare = choice(["contains", "not_contains"])
        value = choice(string.ascii_lowercase)
        return f"{field} {compare} {value}"

    def rule_int(self) -> str:
        field = choice(["Year", "PlayedCount", "PlayedTime"])
        compare = choice(["contains", "not_contains"])
        value = str(randint(0, 9))
        return f"{field} {compare} {value}"
