import logging
import os
import shutil
import subprocess

from textwrap import dedent

from .core import CORE
from .components.zephyr.const import ZEPHYR_BASE, ZEPHYR_CORE_KEY, KCONFIG_KEY
from esphome.helpers import mkdir_p


_LOGGER = logging.getLogger(__name__)


PROJ_DIR = "proj"
BOOT_DIR = "boot"

AUTO_GEN_ZEPHYR_MAIN_BEGIN = "// ========== AUTO GENERATED ZEPHYR MAIN BLOCK BEGIN ==========="
AUTO_GEN_ZEPHYR_MAIN_END = "// ========== AUTO GENERATED ZEPHYR MAIN BLOCK END ==========="


class ZephyrDirectoryBuilder:
    proj_name: str
    zephyr_base: str
    proj_dir: str
    boot_dir: str
    key_file: str

    def __init__(self):
        assert CORE.name is not None
        self.proj_name = CORE.name
        self.zephyr_base = CORE.data[ZEPHYR_CORE_KEY][ZEPHYR_BASE]
        self.proj_dir = CORE.relative_build_path(os.path.join(PROJ_DIR, CORE.name))
        self.boot_dir = CORE.relative_build_path(BOOT_DIR)
        self.key_file = os.path.abspath(CORE.relative_build_path(f"{self.proj_name}.pem"))

    def __enter__(self) -> "ZephyrDirectoryBuilder":
        self._saved_build_path = CORE.build_path
        CORE.build_path = self.proj_dir
        return self

    def __exit__(self, type_, value, traceback):
        CORE.build_path = self._saved_build_path

    def run(self) -> int:
        mkdir_p(self.proj_dir)
        mkdir_p(self.boot_dir)

        try:
            self.setupBootloader()
        except Exception as e:
            print(e)
            return 1

        self.createCmakeFile()
        self.createProjFile()
        self.createAppOverlay()

        return 0

    def createCmakeFile(self) -> None:
        cmakeStr = dedent(
            """cmake_minimum_required(VERSION 3.13.1)

            find_package(Zephyr REQUIRED HINTS $ENV{{ZEPHYR_BASE}})
            project({projName})

            include_directories(src/)
            FILE(GLOB_RECURSE sources_SRC CONFIGURE_DEPENDS src/ "*.h" "*.cpp" "*.c")

            target_sources(app PRIVATE ${{sources_SRC}})
            """  # noqa
        )
        with open(os.path.join(self.proj_dir, "CMakeLists.txt"), "w") as f:
            f.write(
                cmakeStr.format(
                    base_dir=self.zephyr_base, projName=self.proj_name
                )
            )

    def createProjFile(self) -> None:
        mapping = CORE.data[ZEPHYR_CORE_KEY][KCONFIG_KEY]
        #mapping["CONFIG_BOOTLOADER_MCUBOOT"] = "y"
        #mapping['CONFIG_MCUBOOT_SIGNATURE_KEY_FILE'] = f'"{self.key_file}"'
        mapping["CONFIG_GPIO"] = "y"
        result = '\n'.join(f"{key}={value}"
                           for key, value in mapping.items())
        with open(os.path.join(self.proj_dir, "prj.conf"), "w") as f:
            f.write(result)

                    #zephyr,console = &cdc_acm_uart0;
    def createAppOverlay(self) -> None:
        contents = dedent("""/*
             * Copyright (c) 2021 Nordic Semiconductor ASA
             *
             * SPDX-License-Identifier: Apache-2.0
             */

            / {
                chosen {
                    zephyr,shell-uart = &cdc_acm_uart0;
                };
            };

            &zephyr_udc0 {
                cdc_acm_uart0: cdc_acm_uart0 {
                    compatible = "zephyr,cdc-acm-uart";
                    label = "CDC_ACM_0";
                };
            };
        """)
        with open(os.path.join(self.proj_dir, "app.overlay"), "w") as f:
            f.write(contents)

    def setupBootloader(self):
        # create the signing keys if one does not exist
        if not os.path.exists(self.key_file):
            keyProcessResults = subprocess.run(
                [
                    "imgtool",
                    "keygen",
                    "-k",
                    self.key_file,
                    "-t",
                    "rsa-2048",
                ]
            )

            if keyProcessResults.returncode != 0:
                raise Exception("Problem createing signing key")

            # protect the key from accidental deletion
            os.chmod(self.key_file, mode=0o444)

        # always copy the bootloader in case there is a new version
        shutil.copytree(
            os.path.join(self.zephyr_base, "bootloader", "mcuboot"),
            os.path.join(f"{self.boot_dir}", "mcuboot"), dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(".git")
        )

        boot_config_path = os.path.join(self.boot_dir, "mcuboot", "prj.conf")
        with open(boot_config_path, "a") as f:
            config = 'CONFIG_BOOT_SIGNATURE_KEY_FILE="{}.pem"'
            f.write(config.format(os.path.abspath(self.key_file)))


            #const struct device *dev = DEVICE_DT_GET(DT_CHOSEN(zephyr_console));
def add_zephyr_main(text: str) -> str:
    text += "\n" + AUTO_GEN_ZEPHYR_MAIN_BEGIN + "\n"
    text += dedent(r"""void main(void)
        {
            const struct device *dev = DEVICE_DT_GET(DT_CHOSEN(zephyr_shell_uart));

            uint32_t dtr = 0;

            if (!device_is_ready(dev) || usb_enable(NULL)) {
                return;
            }

            /* Poll if the DTR flag was set */
            while (!dtr) {
                    uart_line_ctrl_get(dev, UART_LINE_CTRL_DTR, &dtr);
                    k_sleep(K_MSEC(100));

            }

            setup();
            while (1) {
                loop();
            }
        }
        """)
    text += "\n" + AUTO_GEN_ZEPHYR_MAIN_END + "\n"
    return text
