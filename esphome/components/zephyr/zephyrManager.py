import os

from typing import MutableMapping, Any, Tuple, Union, Iterable, Mapping, Type
from .zephyr_writer import ZephyrDirectoryBuilder

import esphome.config_validation as cv
import esphome.codegen as cg

from esphome.core import CORE
from esphome.util import run_external_process

from .boards import registry, BaseZephyrBoard
from .netUpload import net_upload
from .const import PROJ_DIR, BOOT_DIR
from .utils import at_location

class ZephyrManager:
    def __init__(self,
                 board: str,
                 zephyr_base: str,
                 Kconfigs: MutableMapping[str, Any],
                 flash_args: str
                 ) -> None:
        if board not in registry:
            raise cv.Invalid("Specified board does not appear to be a "
                             f"defined Zephyr board {registry.keys()}",)
        self._board = registry[board](self)
        self.board_name = board
        self._zephyr_base = zephyr_base
        self.Kconfigs = Kconfigs
        self.flash_args = flash_args
        self.device_overlay_list = []
        self.add_Kconfig_vec((("CONFIG_SPI", "n"),
                              ("CONFIG_I2C", "n")))

    @property
    def board(self) -> BaseZephyrBoard:
        return self._board

    @property
    def zephyr_base(self) -> str:
        return self._zephyr_base

    def add_Kconfig(self,
                    config_name: str,
                    config_value: Union[str, int, float, bool]) -> None :
        self.Kconfigs[config_name] = config_value

    def add_Kconfig_vec(self, configs: Iterable[Tuple[str, Any]]) -> None:
        for key, value in configs:
            self.add_Kconfig(key, value)

    def handle_i2c(self, **kwargs) -> Tuple[str, str, str]:
        self.add_Kconfig_vec((("CONFIG_I2C", "y"), ("CONFIG_I2C_SHELL", "n")))
        return self.board.handle_i2c(**kwargs)

    def handle_spi(self, **kwargs) -> Mapping[str, str]:
        self.add_Kconfig("CONFIG_SPI", "y")
        return self.board.handle_spi(**kwargs)

    def handle_adc(self, **kwargs) -> Tuple[str, int]:
        self.add_Kconfig("CONFIG_ADC", "y")
        return self.board.handle_adc(**kwargs)

    def upload(self, config, args, host):
        net_flash = False if "/dev" in host else True
        # get the base path to the project dir
        proj_dir = os.path.abspath(CORE.relative_build_path(PROJ_DIR))

        # check if the bootloader has been flashed already
        boot_info_path = os.path.abspath(CORE.relative_build_path("boot_flashed.info"))
        bootloader = os.path.exists(boot_info_path)

        if net_flash:
            return net_upload(bootloader, proj_dir, host)

        # get the base path to the boot dir
        boot_dir = os.path.abspath(CORE.relative_build_path(BOOT_DIR))

        with at_location(self._zephyr_base):
            result = self.board.upload(self.flash_args, boot_dir, proj_dir,
                                       boot_info_path, bootloader, host)
        return result

    def get_writer(self) -> ZephyrDirectoryBuilder:
        return self.board.get_writer()

    def compile(self):
        # get the base path to the project dir
        proj_dir = os.path.abspath(CORE.relative_build_path(PROJ_DIR))
        # get the base path to the boot dir
        boot_dir = os.path.abspath(CORE.relative_build_path(BOOT_DIR))
        # get the path to the key file
        key_file = os.path.abspath(CORE.relative_build_path(f"{CORE.name}.pem"))
        # check if the bootloader has been flashed already
        boot_info_path = os.path.abspath(CORE.relative_build_path("boot_flashed.info"))
        bootloader = os.path.exists(boot_info_path)
        build_flags = ' '.join(CORE.build_flags)
        with at_location(self._zephyr_base):
            os.environ['ZEPHYR_BASE'] = f"{self._zephyr_base}/zephyr"
            # run the west build command
            build_command = ["west",
                            "build",
                            "-b",
                            self.board_name,
                            "-p",
                            "auto",
                            "-d",
                            os.path.join(proj_dir, "build"),
                            os.path.join(proj_dir, str(CORE.name)),
                            "--",
                            f"-DCMAKE_CXX_FLAGS:='{build_flags}'"
                            ]
            build_command = self.board.pre_compile_application(build_command)
            result = run_external_process(*build_command)

            if result == 0 and not bootloader:
                # build the boot loader
                # run the west build command
                build_command = ["west",
                                "build",
                                "-b",
                                self.board_name,
                                "-p",
                                "auto",
                                "-d",
                                os.path.join(boot_dir, "build"),
                                os.path.join(boot_dir, "mcuboot", "boot", "zephyr"),
                                "--",
                                f'-DCONFIG_BOOT_SIGNATURE_KEY_FILE="{key_file}"',
                                ]
                build_command = self.board.pre_compile_bootloader(build_command)

                result = run_external_process(*build_command)

        return result