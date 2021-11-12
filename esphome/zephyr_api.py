import os

from .components.zephyr.const import ZEPHYR_CORE_KEY, KEY_BOARD, ZEPHYR_BASE
from .core import CORE
from .util import run_external_process

from .zephyr_writer import PROJ_DIR, BOOT_DIR


def run_compile():
    # record the directory we are starting in
    beginning_cwd = os.getcwd()

    # get the base path to the project dir
    proj_dir = os.path.abspath(CORE.relative_build_path(PROJ_DIR))

    # get the base path to the boot dir
    boot_dir = os.path.abspath(CORE.relative_build_path(BOOT_DIR))

    # get the board to build against
    board = str(CORE.data[ZEPHYR_CORE_KEY][KEY_BOARD])

    # change to the zephyr base dir
    base = CORE.data[ZEPHYR_CORE_KEY][ZEPHYR_BASE]
    os.chdir(CORE.data[ZEPHYR_CORE_KEY][ZEPHYR_BASE])

    os.environ['ZEPHYR_BASE'] = f"{base}/zephyr"
    # run the west build command
    build_command = ["west",
                     "build",
                     "-b",
                     board,
                     "-p",
                     "auto",
                     "-d",
                     os.path.join(proj_dir, "build"),
                     os.path.join(proj_dir, str(CORE.name))
                     ]
    result = run_external_process(*build_command)

    if result == 0:

        # build the boot loader
        # run the west build command
        build_command = ["west",
                         "build",
                         "-b",
                         board,
                         "-p",
                         "auto",
                         "-d",
                         os.path.join(boot_dir, "build"),
                         os.path.join(boot_dir, "mcuboot")
                         ]
        result = run_external_process(*build_command)

    # return to the starting directory
    os.chdir(beginning_cwd)

    return result
