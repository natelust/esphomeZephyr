from textwrap import dedent
from typing import Tuple, Mapping, List

from ..nrf52840_base import NRF52840Base, GPIO_0, GPIO_1
from .. import registry

import esphome.config_validation as cv


pinMapping = {
    "D0": (GPIO_0, 25),  # UART TX
    "D1": (GPIO_0, 24),  # UARD RX
    "D2": (GPIO_0, 10),  # NRF2
    "D3": (GPIO_1, 15),  # led1
    "D4": (GPIO_1, 10),  # led2
    "D5": (GPIO_1, 8),
    "D6": (GPIO_0, 7),
    "D7": (GPIO_1, 2),  # button
    "D8": (GPIO_0, 16),  # NeoPixel
    "D9": (GPIO_0, 26),
    "D10": (GPIO_0, 27),
    "D11": (GPIO_0, 6),
    "D12": (GPIO_0, 8),
    "D13": (GPIO_1, 9),
    "D14": (GPIO_0, 4),
    "D15": (GPIO_0, 5),
    "D16": (GPIO_0, 30),
    "D17": (GPIO_0, 28),
    "D18": (GPIO_0, 2),
    "D19": (GPIO_0, 3),
    "D20": (GPIO_0, 29),  # Battery
    "D21": (GPIO_0, 31),  # ARef
    "A0": (GPIO_0, 4),
    "A1": (GPIO_0, 5),
    "A2": (GPIO_0, 30),
    "A3": (GPIO_0, 28),
    "A4": (GPIO_0, 2),
    "A5": (GPIO_0, 3),
    "A6": (GPIO_0, 29),  # Battery
    "A7": (GPIO_0, 31),  # Aref
    "D22": (GPIO_0, 12),  # SDA
    "D23": (GPIO_0, 11),  # SCL
    "D24": (GPIO_0, 15),  # MISO
    "D25": (GPIO_0, 13),  # MOSI
    "D26": (GPIO_0, 14),  # SCK
    "D27": (GPIO_0, 19),  # QSPI CLK
    "D28": (GPIO_0, 20),  # QSPI CS
    "D29": (GPIO_0, 17),  # QSPI Data0
    "D30": (GPIO_0, 22),  # QSPI Data1
    "D31": (GPIO_0, 23),  # QSPI Data2
    "D32": (GPIO_0, 21),  # QSPI Data3
    "D33": (GPIO_0, 9)  # NRF1 (bottom)
}

analogMapping: Mapping[str, int] = {
    "A0": 0,
    "A1": 1,
    "A2": 2,
    "A3": 3,
    "A4": 4,
    "A5": 5,
    "A6": 6,
    "A7": 7,
    "D14": 0,
    "D15": 1,
    "D16": 2,
    "D17": 3,
    "D18": 4,
    "D19": 5,
    "D20": 6,
    "D21": 7,
}


@registry.register("adafruit_feather_nrf52840")
class AdafruitFeatherNrf52840(NRF52840Base):
    def get_writer(self):
        self._manager.add_Kconfig_vec((
        ("CONFIG_NORDIC_QSPI_NOR", "y"),
        ("CONFIG_NORDIC_QSPI_NOR_FLASH_LAYOUT_PAGE_SIZE", 4096),
        ("CONFIG_NORDIC_QSPI_NOR_STACK_WRITE_BUFFER_SIZE", 16),))
        return super().get_writer()

    def __str__(self):
        return "adafruit_feather_nrf52840"

            #writeoc = "pp";
            #readoc = "fastread";
            #writeoc = "pp";
            #quad-enable-bit = < 9 >;
            #quad-enable-requirements = "S2B1v6";

            #readoc = "read4o";
            #writeoc = "pp4o";
            #quad-enable-bit-mask = < 512 >;
    def flash_mapping(self) -> str:
        mapping = dedent("""
        /delete-node/ &slot1_partition;

        &slot0_partition {
            reg = < 0x0000C000 0xce000 >;
        };

        &gd25q16 {
            partitions {
                compatible = "fixed-partitions";
                #address-cells = <1>;
                #size-cells = <1>;


                slot1_partition: partition@0 {
                        label = "image-1";
                        reg = <0x0 0xce000>;
                };
            };
        };
        """)
        return mapping
        """
                header: partition@0 {
                    label = "extra-header";
                    reg = <0x00000000 0x400>;
                };
                partition@ce400 {
                    label = "extra-storage";
                    reg = < 0xce400 0x131c00>;
                };
                """

    def pre_compile_bootloader(self, args: List[str]) -> List[str]:
        #args.extend(("-DCONFIG_BOOT_MAX_IMG_SECTORS=1024",))
        args.extend(("-DCONFIG_MULTITHREADING=y",
                     "-DCONFIG_BOOT_MAX_IMG_SECTORS=256",
                     "-DCONFIG_NORDIC_QSPI_NOR=y",
                     "-DCONFIG_NORDIC_QSPI_NOR_FLASH_LAYOUT_PAGE_SIZE=4096",
                     "-DCONFIG_NORDIC_QSPI_NOR_STACK_WRITE_BUFFER_SIZE=16",
                     "-DCONFIG_LOG_MAX_LEVEL=4",
                     "-DCONFIG_SIZE_OPTIMIZATIONS=y",
                     "-DCONFIG_MCUBOOT_LOG_LEVEL_DBG=y",
                     "-DCONFIG_MCUBOOT_UTIL_LOG_LEVEL_DBG=y"))
        return args

    @property
    def pinMapping(self) -> Mapping[str, Tuple[str, int]]:
        return pinMapping

    @property
    def analogMapping(self) -> Mapping[str, int]:
        return analogMapping

    def i2c_arg_parser(self, kwargs):
        if kwargs['sda'] == 'SDA':
            kwargs['sda'] = "D22"
        if kwargs['scl'] == 'SCL':
            kwargs['scl'] = "D23"
        hardware, device = super().i2c_arg_parser(kwargs)
        return hardware, device
