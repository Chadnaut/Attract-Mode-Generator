from timeit import default_timer as timer

start_time = timer()
import re, os
import multiprocessing as mp
from random import seed, randint, shuffle
from tools.rand import Rand
from tools.utils import mkdir_if_none
from tools.image import generate_wheel, generate_snap

ROM_HEADER = "#Name;Title;Emulator;CloneOf;Year;Manufacturer;Category;Players;Rotation;Control;Status;DisplayCount;DisplayType;AltRomname;AltTitle;Extra;Buttons;Series;Language;Region;Rating"

# -------------------------------------------------------------------------------------
# Helpers


def title_to_romname(title: str) -> str:
    """Long title to short romname"""
    parts = re.sub(r"\([^)]+\)|[^a-z ]", "", title.lower()).strip().split(" ")
    return "".join([p[:2] for p in parts])


def random_romnames(romlist: list, min: float = 0.20, max: float = 0.30) -> list:
    """Return slice of random romnames"""
    shuffle(romlist)
    n = len(romlist)
    roms = [rom[0] for rom in romlist[: randint(int(n * min), int(n * max))]]
    roms.sort()
    return roms


# -------------------------------------------------------------------------------------
# Output matches AM formatting


def generate_config(
    name: str,
    emu_name: str,
    rand: Rand,
) -> str:
    return f"""display {name}
\tlayout               generate-plus
\tromlist              {emu_name}
\tin_cycle             yes
\tin_menu              yes
\tfilter               All
\t\tsort_by              Title
\tfilter               Favourites
\t\trule                 Favourite equals 1
\tfilter               Tagged
\t\trule                 Tags contains {rand.tags(1)[0]}
\tfilter               Rule
\t\trule                 {rand.rule_str()}
\tfilter               Multirule
\t\trule                 {rand.rule_str()}
\t\trule                 {rand.rule_int()}

"""


def generate_emulator(
    name: str,
    snaps_path: str,
    wheels_path: str,
    rand: Rand,
) -> str:
    return f"""executable           C:\\{name}\\{name}.exe
args                 "[romfilename]"
workdir              C:\\{name}
rompath              C:\\{name}\\roms
romext               .zip
system               {rand.system()}
artwork    snap            {snaps_path}
artwork    wheel           {wheels_path}
"""


def generate_rom(
    index: int,
    emulator: str,
    rand: Rand,
) -> list:
    title = rand.title()
    players = rand.players()
    return [
        f"{title_to_romname(title)}{index}",
        title,
        emulator,
        "",
        rand.year(),
        rand.manufacturer(),
        rand.category(),
        f"{players}",
        rand.rotation(),
        ",".join([rand.joystick()] * players),
        rand.status(),
        "1",
        "raster",
        "",
        "",
        "",
        rand.buttons(),
        "",
        rand.language(),
        "",
        "",
    ]


def generate_layout() -> str:
    return """// Basic layout with snap & wheel artwork
local flw = ::fe.layout.width;
local flh = ::fe.layout.height;

local bg = ::fe.add_artwork("snap", 0, 0, flw, flh);
local header = ::fe.add_text("[DisplayName] - [FilterName]", 0, 0, flw, flh/20);
local title = ::fe.add_artwork("wheel", 0, flh/20, flw, flh*9/20);
local list = ::fe.add_listbox(0, flh/2, flw, flh/2);
local snap1 = ::fe.add_artwork("snap", 0, flh*11/20, flw/4, flh*8/20);
local snap2 = ::fe.add_artwork("snap", flw*3/4, flh*11/20, flw/4, flh*8/20);

bg.alpha = 64;
title.preserve_aspect_ratio = true;
snap1.preserve_aspect_ratio = true;
snap2.preserve_aspect_ratio = true;
list.set_selbg_rgb(255, 0, 0);

::fe.add_signal_handler("on_signal");
function on_signal(signal) {
    if (signal == "custom1") ::fe.signal("reload");
    return false;
}
"""


def generate_display(
    name: str,
    limit: int,
    emulators_path: str,
    romlists_path: str,
    stats_path: str,
    snaps_path: str,
    wheels_path: str,
    cfg_header: str,
    snap: bool,
    wheel: bool,
    basic: bool,
    rand: Rand,
    randomize: bool,
):
    try:
        if not randomize:
            seed(name)
        emulator = generate_emulator(name, snaps_path, wheels_path, rand)
        romlist = [generate_rom(i, name, rand) for i in range(limit)]

        # print on same line to indicate activity
        print(name, end="\r", flush=True)

        # artwork
        if wheel or snap:
            for rom in romlist:
                rom_name = rom[0]
                rom_title = rom[1]
                print(rom_title.ljust(50), end="\r", flush=True)
                if wheel:
                    if not randomize:
                        seed(rom_name)
                    generate_wheel(rom_name, rom_title, wheels_path, rand)
                if snap:
                    if not randomize:
                        seed(rom_name)
                    generate_snap(rom_name, basic, snaps_path, rand)

        # clears the line
        print("\033[K", end="\r", flush=True)

        # romlist
        with open(os.path.join(romlists_path, f"{name}.txt"), "w") as file:
            file.write(ROM_HEADER + "\n")
            for rom in romlist:
                line = ";".join(rom)
                file.write(f"{line}\n")

        # emulator
        with open(os.path.join(emulators_path, f"{name}.cfg"), "w") as file:
            file.write(cfg_header + emulator)

        # favourites
        with open(os.path.join(romlists_path, f"{name}.tag"), "w") as file:
            file.write("\n".join(random_romnames(romlist)))

        # tags
        for tag in rand.tags(randint(2, 4)):
            mkdir_if_none(os.path.join(romlists_path, name))
            with open(os.path.join(romlists_path, name, f"{tag}.tag"), "w") as file:
                file.write("\n".join(random_romnames(romlist)))

        # stats
        mkdir_if_none(os.path.join(stats_path, name))
        for romname in random_romnames(romlist):
            with open(os.path.join(stats_path, name, f"{romname}.stat"), "w") as file:
                file.write(f"{randint(0, 100)}\n{randint(100, 10000)}\n")

    except (KeyboardInterrupt, SystemExit):
        return

    except Exception as err:
        print(err)
        return


# -------------------------------------------------------------------------------------


def generate(
    output: str = "",
    config: str = "",
    displays: int = 10,
    roms: int = 1000,
    single_thread: bool = False,
    snap: bool = False,
    wheel: bool = False,
    basic: bool = False,
    version: str = "",
    randomize: bool = False,
):
    config_path = mkdir_if_none(output)
    emulators_path = mkdir_if_none(os.path.join(config_path, "emulators", ""))
    romlists_path = mkdir_if_none(os.path.join(config_path, "romlists", ""))
    stats_path = mkdir_if_none(os.path.join(config_path, "stats", ""))
    image_path = mkdir_if_none(os.path.join(config_path, "images", ""))
    snaps_path = mkdir_if_none(os.path.join(image_path, "snap", ""))
    wheels_path = mkdir_if_none(os.path.join(image_path, "wheel", ""))
    layout_path = mkdir_if_none(os.path.join(config_path, "layouts", ""))
    generate_layout_path = mkdir_if_none(os.path.join(layout_path, "generate-plus", ""))
    cfg_header = f"# Generated by {version}\n#\n"

    rand = Rand(os.path.join(os.getcwd(), config))
    display_limit = min(1000, displays)
    rom_limit = min(100000, roms)
    display_names = [f"Display{i}" for i in range(0, display_limit)]
    emulator_names = [f"Emulator{i}" for i in range(0, display_limit)]

    config = [
        generate_config(name, emulator_names[i], rand)
        for i, name in enumerate(display_names)
    ]
    with open(os.path.join(config_path, "attract.cfg"), "w") as file:
        file.write(cfg_header + "".join(config))

    with open(os.path.join(generate_layout_path, "layout.nut"), "w") as file:
        file.write(cfg_header.replace("#", "//") + generate_layout())

    args = (
        rom_limit,
        emulators_path,
        romlists_path,
        stats_path,
        snaps_path,
        wheels_path,
        cfg_header,
        snap,
        wheel,
        basic,
        rand,
        randomize,
    )

    if single_thread:
        for name in emulator_names:
            generate_display(name, *args)
    else:
        with mp.Pool() as pool:
            pool.starmap(
                generate_display,
                ((name, *args) for name in emulator_names),
            )

    print(
        f"Generated {display_limit * rom_limit} roms in {((timer() - start_time) * 1000):.3f} ms"
    )
