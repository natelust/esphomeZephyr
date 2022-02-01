from __future__ import annotations
import logging
import os
import shutil
import subprocess

from typing import TYPE_CHECKING

from textwrap import dedent

from esphome.core import CORE
from .const import ZEPHYR_BASE, ZEPHYR_CORE_KEY, KCONFIG_KEY
from esphome.helpers import mkdir_p


if TYPE_CHECKING:
    from esphome.components.zephyr import ZephyrManager

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

    def __init__(self, manager: ZephyrManager):
        assert CORE.name is not None
        self.proj_name = CORE.name
        self.manager = manager
        self.zephyr_base = self.manager.zephyr_base
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
        self.createAppOverlayBoot()

        return 0

            #set(CMAKE_BUILD_TYPE DEBUG)
            #set(CMAKE_CXX_FLAGS_DEBUG "${{CMAKE_CXX_FLAGS_DEBUG}} -O0")
            #set(CMAKE_C_FLAGS_DEBUG "${{CMAKE_C_FLAGS_DEBUG}} -O0")
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
        self.manager.add_Kconfig_vec((
            ("CONFIG_BOOTLOADER_MCUBOOT", "y"),
            ('CONFIG_MCUBOOT_SIGNATURE_KEY_FILE', f'"{self.key_file}"'),
        ))
        result = '\n'.join(f"{key}={value}"
                           for key, value in self.manager.Kconfigs.items())
        with open(os.path.join(self.proj_dir, "prj.conf"), "w") as f:
            f.write(result)

    def createAppOverlayBoot(self) -> None:
        contents = self.manager.board.flash_mapping()
        with open(os.path.join(self.boot_dir, "mcuboot", "boot", "zephyr", "dts.overlay"), "a") as f:
            f.write(contents)

                    #zephyr,console = &cdc_acm_uart0;
    def createAppOverlay(self) -> None:
        contents = dedent("""
            /*
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
        contents += self.manager.board.flash_mapping()
        contents = '\n'.join((contents, *self.manager.device_overlay_list))

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

        boot_config_path = os.path.join(self.boot_dir, "mcuboot", "boot", "zephyr", "prj.conf")
        with open(boot_config_path, "a") as f:
            config = 'CONFIG_BOOT_SIGNATURE_KEY_FILE="{}"\n'
            f.write(config.format(os.path.abspath(self.key_file)))


            #const struct device *dev = DEVICE_DT_GET(DT_CHOSEN(zephyr_console));
def add_zephyr_main(text: str) -> str:
    text += AUTO_GEN_ZEPHYR_MAIN_BEGIN + "\n"
    text += dedent(r"""#include <mgmt/mcumgr/smp_udp.h>
#include <net/net_mgmt.h>
#include <net/net_event.h>
#include <net/net_conn_mgr.h>

#define LOG_LEVEL LOG_LEVEL_DBG
#include <logging/log.h>

#include "img_mgmt/img_mgmt.h"
#include "os_mgmt/os_mgmt.h"

LOG_MODULE_REGISTER(smp_udp_sample);

#define EVENT_MASK (NET_EVENT_L4_CONNECTED | NET_EVENT_L4_DISCONNECTED)

static struct net_mgmt_event_callback mgmt_cb;

static void event_handler(struct net_mgmt_event_callback *cb,
			  uint32_t mgmt_event, struct net_if *iface)
{
	if ((mgmt_event & EVENT_MASK) != mgmt_event) {
		return;
	}

	if (mgmt_event == NET_EVENT_L4_CONNECTED) {
		LOG_INF("Network connected");

		if (smp_udp_open() < 0) {
			LOG_ERR("could not open smp udp");
		}

		return;
	}

	if (mgmt_event == NET_EVENT_L4_DISCONNECTED) {
		LOG_INF("Network disconnected");
		smp_udp_close();
		return;
	}
}

void start_smp_udp(void)
{
	net_mgmt_init_event_callback(&mgmt_cb, event_handler, EVENT_MASK);
	net_mgmt_add_event_callback(&mgmt_cb);
	net_conn_mgr_resend_status();
}
        void main(void)
        {
            const struct device *dev = DEVICE_DT_GET(DT_CHOSEN(zephyr_shell_uart));

            uint32_t dtr = 0;

            if (!device_is_ready(dev) || usb_enable(NULL)) {
                return;
            }

            /* Poll if the DTR flag was set */
            /*
            while (!dtr) {
                    uart_line_ctrl_get(dev, UART_LINE_CTRL_DTR, &dtr);
                    k_sleep(K_MSEC(100));

            }
            */
//#ifdef USE_ZEPHYR_OTA
            start_smp_udp();
            img_mgmt_register_group();
            os_mgmt_register_group();
//#endif
            setup();
            printk("hello world\n");
            while (1) {
                loop();
            }
        }
        """)
    # This bit is for openthread, refactor this all later
    text += "\n" + AUTO_GEN_ZEPHYR_MAIN_END + "\n"
    return text
