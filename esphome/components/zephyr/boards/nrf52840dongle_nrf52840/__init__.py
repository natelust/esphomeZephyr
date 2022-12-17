from __future__ import annotations
import os
from shutil import which
from textwrap import dedent
from typing import Tuple, Mapping, TYPE_CHECKING, List

from esphome.util import run_external_process

from ..nrf52840_base import NRF52840Base, GPIO_0, GPIO_1
from .. import registry

from .writer import DongleDirectoryBuilder

import esphome.config_validation as cv

if TYPE_CHECKING:
    from ...zephyr_writer import ZephyrDirectoryBuilder


# Note, there are other pads on the bottom that are not added here yet
pinMapping = {
    "P0.13": (GPIO_0, 13),
    "P0.15": (GPIO_0, 15),
    "P0.17": (GPIO_0, 17),
    "P0.20": (GPIO_0, 20),  # UART TX
    "P0.22": (GPIO_0, 22),  # QSPI
    "P0.24": (GPIO_0, 24),  # UART RX
    "P1.00": (GPIO_1, 0),  # QSPI, TRACEDATA, Serial wire out (SWO)
    "P0.09": (GPIO_0, 9),  # NFC1 NFC antenna connection
    "P0.10": (GPIO_0, 10),  # NFC2 NFC antenna connection
    "P0.31": (GPIO_0, 31),  # analog input 7
    "P0.29": (GPIO_0, 29),  # analog input 5
    "P0.02": (GPIO_0, 2),  # analog input 0
    "P1.15": (GPIO_1, 15),
    "P1.13": (GPIO_1, 13),
    "P1.10": (GPIO_1, 10),
    "P0.06": (GPIO_0, 6),  # Green LED
    "P0.08": (GPIO_0, 8),  # Red LED (RGB)
    "P1.09": (GPIO_1, 9),  # Greed LED (RGB)
    "P0.12": (GPIO_0, 12),  # Blue LED  (RGB)
    "P1.06": (GPIO_1, 6),  # Button 1
    "P0.18": (GPIO_0, 18),  # Reset button
}

analogMapping: Mapping[str, int] = {
    "A0": 0,
    "A5": 5,
    "A7": 7,
    "P0.02": 0,
    "P0.29": 5,
    "P0.031": 7,
}


@registry.register("nrf52840dongle_nrf52840")
class NRF52840Dongle(NRF52840Base):
    def __str__(self):
        return "nrf52840dongle_nrf52840"

    def flash_mapping(self) -> str:
        mapping = dedent("""
            /delete-node/ &boot_partition;
            /delete-node/ &slot0_partition;
            /delete-node/ &slot1_partition;
            /delete-node/ &storage_partition;
            /delete-node/ &scratch_partition;

            / {
                chosen {
                    zephyr,code-partition = &CODE_PARTITION;
                };
            };

            &flash0 {
                partitions {
                    compatible = "fixed-partitions";
                    #address-cells = < 0x1 >;
                    #size-cells = < 0x1 >;
                    newboot_partition: partition@1000 {
                            label = "mcuboot";
                            reg = < 0x1000 0x000f000 >;
                    };
                    newcode: partition@10000 {
                            label = "image-0";
                            reg = < 0x10000 0x66000 >;
                    };
                    partition@76000 {
                            label = "image-1";
                            reg = < 0x76000 0x66000 >;
                    };
                    partition@dc000 {
                            label = "storage";
                            reg = < 0xdc000 0x4000 >;
                    };
                };
            };
            """)
        return mapping

    def pre_compile_bootloader(self, args: List[str]) -> List[str]:
        args.extend([
            "-DCONFIG_BOOT_ERASE_PROGRESSIVELY=n",
            "-DCONFIG_BOOT_UPGRADE_ONLY=y",
            #"-DCONFIG_LOG=y",
            #         "-DCONFIG_DEBUG=n",
            #         "-DCONFIG_MBEDTLS_AES_ROM_TABLES=n",
            #         "-DCONFIG_UART_CONSOLE=y",
            #         "-DCONFIG_CONSOLE=y",
        ])
        return args

    def pre_compile_application(self, args: List[str]) -> List[str]:
        # Flash space is at a premium, dont use space for zephyr log strings,
        # except critical ones
        args.extend(['--', '-DCONFIG_LOG_MAX_LEVEL=2'])
        return args

    @property
    def pinMapping(self) -> Mapping[str, Tuple[str, int]]:
        return pinMapping

    @property
    def analogMapping(self) -> Mapping[str, int]:
        return analogMapping

    def i2c_arg_parser(self, kwargs) -> Tuple[bool, str]:
        if kwargs['sda'] == 'SDA':
            raise cv.Invalid(f"{self} requires a pin to be selected for sda")
        if kwargs['scl'] == 'SCL':
            raise cv.Invalid(f"{self} requires a pin to be selected for scl")
        if kwargs['sda'] not in pinMapping:
            raise cv.Invalid(f"{kwargs['sda']} is not a valid pin identifier")
        if kwargs['scl'] not in pinMapping:
            raise cv.Invalid(f"{kwargs['scl']} is not a valid pin identifier")
        hardware, device = super().i2c_arg_parser(kwargs)

        return hardware, device

    def get_writer(self) -> ZephyrDirectoryBuilder:
        return DongleDirectoryBuilder(self._manager)

    def upload(self, flash_args: str, boot_dir: os.PathLike,
               proj_dir: os.PathLike, boot_info_path: os.PathLike,
               bootloader: bool, host: str):
        if which("mcumgr") is None or which("nrfutil") is None:
            raise ValueError(f"mcumgr and nrfutil must be installed to upload to {self}")
        if not bootloader:
            args = ["nrfutil",
                    "pkg",
                    "generate",
                    "--hw-version",
                    "52",
                    "--sd-req=0x00",
                    "--application",
                    f"{boot_dir}/build/zephyr/zephyr.hex",
                    "--application-version",
                    "1",
                    f"{boot_dir}/build/zephyr/mcuboot.zip"]
            result = run_external_process(*args)
            if result != 0:
                print("Creating boot image failed")
                return result
            install_args = ["nrfutil",
                            "dfu",
                            "usb-serial",
                            "-pkg",
                            f"{boot_dir}/build/zephyr/mcuboot.zip",
                            "-p",
                            f"{host}",
                            "-b",
                            "1000000"]
            result = run_external_process(*install_args)
            if result != 0:
                print("Uploading boot image failed, is your device in reset mode")
                return result
            print("Bootloader installed, unplug the device, plug it back in with the"
                  " software button held down, and re-run upload")
            with open(boot_info_path, 'w') as f:
                f.write("")
            return -1

        print("### FLASHING APPLICATION #####")
                      #f"--connstring=dev={host},baud=115200",
                      #f"--connstring=dev={host},baud=115200,mtu=512",
        image_args = ["mcumgr",
                      "--conntype=serial",
                      f"--connstring=dev={host},baud=115200,mtu=512",
                      "image",
                      "upload",
                      "-e",
                      f"{proj_dir}/build/zephyr/zephyr.signed.bin"
                      ]
        result = run_external_process(*image_args)
        if result != 0:
            print("failed to upload image, is your board in boot mode?")
            return result

        restart_args = ["mcumgr",
                        "--conntype=serial",
                        f"--connstring=dev={host},baud=115200",
                        "reset"
                        ]
        result = run_external_process(*restart_args)
        if result != 0:
            print("Failed to restart device through serial connection")
        return result
