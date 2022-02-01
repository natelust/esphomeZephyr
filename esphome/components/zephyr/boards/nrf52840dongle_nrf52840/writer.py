import os
from textwrap import dedent
from ...zephyr_writer import ZephyrDirectoryBuilder


CONTENTS = dedent("""
    &zephyr_udc0 {
        cdc_acm_uart0: cdc_acm_uart0 {
            compatible = "zephyr,cdc-acm-uart";
            label = "CDC_ACM_0";
        };
    };

""")


class DongleDirectoryBuilder(ZephyrDirectoryBuilder):
    def createAppOverlayBoot(self) -> None:
        contents = self.manager.board.flash_mapping()
        contents = contents.replace("CODE_PARTITION", "newboot_partition")
        contents += CONTENTS
        with open(os.path.join(self.boot_dir, "mcuboot", "boot", "zephyr", "dts.overlay"), "a") as f:
            f.write(contents)

    def createAppOverlay(self) -> None:
        contents = '\n'.join((CONTENTS, *self.manager.device_overlay_list))
        contents += self.manager.board.flash_mapping()
        contents = contents.replace("CODE_PARTITION", "newcode")
        contents += CONTENTS
        contents += dedent("""
            / {
                chosen {
                    zephyr,shell-uart = &cdc_acm_uart0;
                };
            };
        """)
        with open(os.path.join(self.proj_dir, "app.overlay"), "w") as f:
            f.write(contents)