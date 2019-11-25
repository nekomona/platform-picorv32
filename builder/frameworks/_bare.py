from SCons.Script import Import

Import("env")

board = env.BoardConfig()

env.Append(

    ASFLAGS = ["-x", "assembler-with-cpp"],

    CCFLAGS=[
        # "-Os",
        # "-Wall", 
        "-march=%s" % board.get("build.march"),
        "-mabi=%s" % board.get("build.mabi"),
        # "-mcmodel=%s" % board.get("build.mcmodel"),
        # "-fmessage-length=0",
        # "-fsigned-char",
        "--specs=nosys.specs",
        "-ffunction-sections",
        "-fdata-sections",
        "-fno-unwind-tables",
        # "-fno-common",
        # "-ffreestanding",
        # "-nostdlib"
    ],

    CFLAGS = [
        "-std=gnu11"
    ],

    CXXFLAGS = [
        "-std=gnu++17",
        "-fno-rtti"
    ],

    CPPDEFINES = [
    ],

    LINKFLAGS=[
        "-march=%s" % board.get("build.march"),
        "-mabi=%s" % board.get("build.mabi"),
        # "-mcmodel=%s" % board.get("build.mcmodel"),
        "-Bstatic",
        "-nostartfiles",
        # "-Xlinker",
        # "--gc-sections",
        # "--specs=nano.specs"
        # "-Wl,--wrap=_exit",
        # "-Wl,--wrap=close",
        # "-Wl,--wrap=fatat",
        # "-Wl,--wrap=isatty",
        # "-Wl,--wrap=lseek",
        # "-Wl,--wrap=read",
        # "-Wl,--wrap=sbrk",
        # "-Wl,--wrap=stub",
        # "-Wl,--wrap=write_hex",
        # "-Wl,--wrap=write"
    ],

    LIBS=["c"]
)


# copy CCFLAGS to ASFLAGS (-x assembler-with-cpp mode)
env.Append(ASFLAGS=env.get("CCFLAGS", [])[:])
