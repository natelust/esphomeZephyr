import os
import re
import subprocess

from typing import Union, Any

from esphome.util import run_external_process
from esphome.core import CORE

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


def net_upload(bootloader: bool, proj_dir: os.PathLike, address:str) -> Union[int, bytes, Any]:
        if not bootloader:
            print("Cannot use net flash if bootloader was not previously flashed")
            return 1
        flash_args = ["mcumgr",
                      "--conntype",
                      "udp",
                      f"--connstring=[{address}]:1337",
                      "image",
                      "upload",
                      "-e",
                      f"{os.path.join(proj_dir, 'build', 'zephyr' '/zephyr.signed.confirmed.bin')}"
                      ]
        result = run_external_process(*flash_args)
        if result != 0:
            return result
        #list_args = ["mcumgr",
        #             "--conntype",
        #             "udp",
        #             f"--connstring=[{address}]:1337",
        #             "image",
        #             "list",
        #             ]
        #command = subprocess.run(list_args, capture_output=True)
        #if command.returncode != 0:
        #    return command.returncode
        #output = command.stdout.decode()
        #hashes = re.findall(r"^.*hash[:] ([A-Za-z0-9]*)$", output, re.MULTILINE)
        #confirm_args = ["mcumgr",
        #                "--conntype",
        #                "udp",
        #                f"--connstring=[{address}]:1337",
        #                "image",
        #                "confirm",
        #                f"{hashes[-1]}"
        #                ]
        #value = run_external_process(*confirm_args)
        #if value != 0:
        #    return value
        restart_args = ["mcumgr",
                        "--conntype",
                        "udp",
                        f"--connstring=[{address}]:1337",
                        "reset"
                        ]
        value = run_external_process(*restart_args)

        return value