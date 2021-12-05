import re
import os
import subprocess

from .core import CORE
from .util import run_external_process

from .zephyr_writer import PROJ_DIR, BOOT_DIR


def get_flash_address() -> str:
    from ipaddress import IPv6Address
    from time import sleep
    from zeroconf import ServiceBrowser, ServiceStateChange, Zeroconf

    def on_service_state_change(zeroconf, service_type, name, state_change):
        if state_change is ServiceStateChange.Added:
            zeroconf.get_service_info(service_type, name)

    zc = Zeroconf()
    ServiceBrowser(zc, "_esphomelib._tcp.local.", handlers=[on_service_state_change])
    sleep(1)
    entry = zc.cache.entries_with_name(f'{CORE.name}.local.')
    zc.close()
    if entry:
        for en in entry:
            if hasattr(en, 'address'):
                return str(IPv6Address(en.address))
    raise RuntimeError("Cannont find address to use in net flashing")


def run_upload(config, args, host, net_flash):
    # record the directory we are starting in
    beginning_cwd = os.getcwd()

    # get the base path to the project dir
    proj_dir = os.path.abspath(CORE.relative_build_path(PROJ_DIR))

    # get the base path to the boot dir
    boot_dir = os.path.abspath(CORE.relative_build_path(BOOT_DIR))

    # check if the bootloader has been flashed already
    boot_info_path = os.path.abspath(CORE.relative_build_path("boot_flashed.info"))
    bootloader = os.path.exists(boot_info_path)

    if net_flash:
        if not bootloader:
            print("Cannot use net flash if bootloader was not previously flashed")
            return 1
        address = get_flash_address()
        flash_args = ["mcumgr",
                      "--conntype",
                      "udp",
                      f"--connstring=[{address}]:1337",
                      "image",
                      "upload",
                      "-e",
                      f"{os.path.join(proj_dir, 'build', 'zephyr' '/zephyr.signed.bin')}"
                      ]
        result = run_external_process(*flash_args)
        if result != 0:
            return result
        list_args = ["mcumgr",
                     "--conntype",
                     "udp",
                     f"--connstring=[{address}]:1337",
                     "image",
                     "list",
                     ]
        command = subprocess.run(list_args, capture_output=True)
        if command.returncode != 0:
            return command.returncode
        output = command.stdout.decode()
        hashes = re.findall(r"^.*hash[:] ([A-Za-z0-9]*)$", output, re.MULTILINE)
        confirm_args = ["mcumgr",
                        "--conntype",
                        "udp",
                        f"--connstring=[{address}]:1337",
                        "image",
                        "confirm",
                        f"{hashes[-1]}"
                        ]
        value = run_external_process(*confirm_args)
        if value != 0:
            return value
        restart_args = ["mcumgr",
                        "--conntype",
                        "udp",
                        f"--connstring=[{address}]:1337",
                        "reset"
                        ]
        return run_external_process(*restart_args)


    base = CORE.zephyr_manager._zephyr_base
    os.chdir(base)

    flash_args = ["west",
                  "flash",
                  "-d",
                  os.path.join(boot_dir, "build"),
                  ]
    # replace any placehonders for build_dir
    extra_args_str = CORE.zephyr_manager.flash_args

    if not bootloader:
        boot_extra_args_str = extra_args_str.replace("BUILD_DIR", flash_args[3])
        boot_flash_args = flash_args + boot_extra_args_str.split()
        print("### FLASHING BOOTLOADER #####")
        result = run_external_process(*boot_flash_args)
        if result != 0:
            return result
        with open(boot_info_path, 'w') as f:
            f.write("")

    print("### FLASHING APPLICATION #####")
    flash_args[3] = os.path.join(proj_dir, "build")
    app_extra_args_str = extra_args_str.replace("BUILD_DIR", flash_args[3])
    app_flash_args = flash_args + app_extra_args_str.split()
    print(f"Running {app_flash_args}")
    result = run_external_process(*app_flash_args)

    os.chdir(beginning_cwd)
    return result


def run_compile():
    # record the directory we are starting in
    beginning_cwd = os.getcwd()

    # get the base path to the project dir
    proj_dir = os.path.abspath(CORE.relative_build_path(PROJ_DIR))

    # get the base path to the boot dir
    boot_dir = os.path.abspath(CORE.relative_build_path(BOOT_DIR))

    # get the path to the key file
    key_file = os.path.abspath(CORE.relative_build_path(f"{CORE.name}.pem"))

    # get the board to build against
    board = CORE.zephyr_manager.board_name

    # change to the zephyr base dir
    base = CORE.zephyr_manager._zephyr_base
    os.chdir(base)

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
                     os.path.join(proj_dir, str(CORE.name)),
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
                         os.path.join(boot_dir, "mcuboot", "boot", "zephyr"),
                         "--",
                         f'-DCONFIG_BOOT_SIGNATURE_KEY_FILE="{key_file}"',
                         ]
        result = run_external_process(*build_command)
                         #'-DBOARD_FLASH_RUNNER=blackmagicprobe',
                         #'-DBOARD_DEBUG_RUNNER=blackmagicprobe'

    # return to the starting directory
    os.chdir(beginning_cwd)

    return result
