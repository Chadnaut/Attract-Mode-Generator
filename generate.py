# nuitka-project: --onefile
# nuitka-project: --standalone
# nuitka-project: --windows-icon-from-ico=data/icons/icon.png
# nuitka-project: --linux-icon=data/icons/icon.png
# nuitka-project: --macos-app-icon=data/icons/icon.png
# nuitka-project: --no-deployment-flag=self-execution

if __name__ == "__main__":
    import sys, os, shutil
    from optparse import OptionParser

    version = "Generate-Plus 0.0.2"
    parser = OptionParser(
        description=f"{version} creates a series of config files for debugging.",
        version=version,
    )

    parser.add_option(
        "-o",
        "--output",
        type=str,
        help="output path to generate files",
    )
    parser.add_option(
        "-d",
        "--displays",
        type=int,
        default=10,
        help="number of displays to generate",
    )
    parser.add_option(
        "-r",
        "--roms",
        type=int,
        default=100,
        help="number of roms to generate",
    )
    parser.add_option(
        "-w",
        "--wheel",
        action="store_true",
        help="generate wheel artwork",
    )
    parser.add_option(
        "-s",
        "--snap",
        action="store_true",
        help="generate snap artwork",
    )
    parser.add_option(
        "-b",
        "--basic",
        action="store_true",
        help="basic snap artwork (fast)",
    )
    parser.add_option(
        "-c",
        "--config",
        type=str,
        default="data/json/generate.json",
        help="config json for generator",
    )
    parser.add_option(
        "-f",
        "--force",
        action="store_true",
        help="overwrite output",
    )
    parser.add_option(
        "-t",
        "--single-thread",
        action="store_true",
        help="single-thread mode",
    )
    parser.add_option(
        "-z",
        "--randomize",
        action="store_true",
        help="randomize results",
    )

    args, other = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()

    elif args.output:
        if not args.output:
            print("ERROR: Output path required, use --output <path>")
            sys.exit(1)

        args.output = os.path.realpath(os.path.join(os.getcwd(), args.output))

        if os.path.isdir(args.output):
            files = next(os.walk(args.output), ([], [], []))[2]
            apps = ["attract.exe", "attractplus.exe", "attract.bin", "attractplus.bin"]
            if set(files) & set(apps):
                print("ERROR: Cannot use AM path")
                sys.exit(1)

            if not args.force:
                print("ERROR: Output path exists, use --force to overwrite")
                sys.exit(1)

        # Guestimate required space
        available = shutil.disk_usage(os.path.dirname(args.output))[2]
        total_roms = args.displays * args.roms
        req_conf = 900 + (args.displays * 1250) + (total_roms * 165)
        req_snap = (total_roms * 57000) if args.snap else 0
        req_wheel = (total_roms * 51000) if args.wheel else 0
        required = req_conf + req_snap + req_wheel
        if required > available:
            print(f"ERROR: Not enough disk space, require {required} MB")
            sys.exit(1)

        from app.generate import generate

        generate(
            output=args.output,
            config=args.config,
            displays=args.displays,
            roms=args.roms,
            snap=args.snap,
            wheel=args.wheel,
            basic=args.basic,
            single_thread=args.single_thread,
            version=version,
            randomize=args.randomize,
        )
