import sys
from os.path import join

from SCons.Script import (ARGUMENTS, COMMAND_LINE_TARGETS, AlwaysBuild,
                          Default, DefaultEnvironment)


env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

env.Replace(
    AR="riscv-none-embed-gcc-ar",
    AS="riscv-none-embed-as",
    CC="riscv-none-embed-gcc",
    GDB="riscv-none-embed-gdb",
    CXX="riscv-none-embed-g++",
    OBJCOPY="riscv-none-embed-objcopy",
    RANLIB="riscv-none-embed-gcc-ranlib",
    SIZETOOL="riscv-none-embed-size",

    ARFLAGS=["rc"],

    SIZEPRINTCMD='$SIZETOOL -d $SOURCES',

    PROGSUFFIX=".elf"
)

# Allow user to override via pre:script
if env.get("PROGNAME", "program") == "program":
    env.Replace(PROGNAME="firmware")

env.Append(
    BUILDERS=dict(
        ElfToBin=Builder(
            action=env.VerboseAction(" ".join([
                "$OBJCOPY",
                "-O",
                "binary",
                "$SOURCES",
                "$TARGET"
            ]), "Building $TARGET"),
            suffix=".bin"
        ),
        ElfToHex=Builder(
            action=env.VerboseAction(" ".join([
                "$OBJCOPY",
                "-O",
                "ihex",
                "$SOURCES",
                "$TARGET"
            ]), "Building $TARGET"),
            suffix=".hex"
        ),
        ElfToOut=Builder(
            action=env.VerboseAction(" ".join([
                "$OBJCOPY",
                "-O",
                "verilog",
                "$SOURCES",
                "$TARGET"
            ]), "Building $TARGET"),
            suffix=".out"
        )
    )
)

if not env.get("PIOFRAMEWORK"):
    env.SConscript("frameworks/_bare.py", exports="env")

#
# Target: Build executable and linkable firmware
#

target_elf = None
if "nobuild" in COMMAND_LINE_TARGETS:
    target_elf = join("$BUILD_DIR", "${PROGNAME}.elf")
    target_firm = join("$BUILD_DIR", "${PROGNAME}.bin")
    target_hex = join("$BUILD_DIR", "${PROGNAME}.hex")
    target_out = join("$BUILD_DIR", "${PROGNAME}.out")
else:
    target_elf = env.BuildProgram()
    target_firm = env.ElfToBin(join("$BUILD_DIR", "${PROGNAME}"), target_elf)
    target_hex = env.ElfToHex(join("$BUILD_DIR", "${PROGNAME}"), target_elf)
    target_out = env.ElfToOut(join("$BUILD_DIR", "${PROGNAME}"), target_elf)

AlwaysBuild(env.Alias("nobuild", target_firm))
target_buildprog = env.Alias("buildprog", target_firm, target_firm)
target_buildhex = env.Alias("buildhex", target_hex, target_hex)
target_buildout = env.Alias("buildout", target_out, target_out)

#
# Target: Print binary size
#

target_size = env.Alias(
    "size", target_elf,
    env.VerboseAction("$SIZEPRINTCMD", "Calculating size $SOURCE"))
AlwaysBuild(target_size)


#
# Target: Upload by default .elf file
#
upload_protocol = env.subst("$UPLOAD_PROTOCOL")
debug_tools = board.get("debug.tools", {})
upload_source = target_firm
upload_actions = []

if upload_protocol == "serial":
    # def __configure_upload_port(env):
    #     return basename(env.subst("$UPLOAD_PORT"))

    env.Replace(
        # __configure_upload_port=__configure_upload_port,
        UPLOADER="pico-programmer",
        UPLOADERFLAGS=[
        ],
        #UPLOADCMD='$UPLOADER $UPLOADERFLAGS "$SOURCE" "${__configure_upload_port(__env__)}"'
        UPLOADCMD='$UPLOADER $UPLOADERFLAGS "$SOURCE" "$UPLOAD_PORT"'
    )
    upload_source = target_out
    upload_actions = [
        env.VerboseAction(env.AutodetectUploadPort, "Looking for upload port..."),
        env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")
    ]
    
# custom upload tool
elif upload_protocol == "custom":
    upload_actions = [env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")]

else:
    sys.stderr.write("Warning! Unknown upload protocol %s\n" % upload_protocol)

AlwaysBuild(env.Alias("upload", upload_source, upload_actions))


#
# Setup default targets
#

Default([target_buildprog, target_buildhex, target_size])
