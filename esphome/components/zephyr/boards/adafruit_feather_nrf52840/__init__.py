from typing import Tuple

from ..baseBoardValidator import BaseZephyrBoard
from .. import registry

GPIO_0 = "gpio0"
GPIO_1 = "gpio1"

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


@registry.register("adafruit_feather_nrf52840")
class AdafruitFeatherNrf52840(BaseZephyrBoard):
    @classmethod
    def SDA_PIN(cls) -> str:
        return "D22"

    @classmethod
    def SCL_PIN(cls) -> str:
        return "D23"

    @classmethod
    def validate_gpio_pin(cls, value):
        # do nothing for now, fix this later
        return value

    @classmethod
    def validate_supports(cls, value):
        # do nothing for now, fix this later
        return value

    @classmethod
    def get_device_and_pin(cls, pin):
        value = pinMapping.get(pin)
        if value is None:
            raise NotImplementedError(f"Cannot handle pin specifier {pin}, "
                                      f"must be one of {pinMapping.keys()}")
        return value

    @classmethod
    def can_openthread(cls) -> bool:
        return True

    @classmethod
    def i2c_arg_validator(cls, **kwargs):
        if kwargs['sda'] == cls.SDA_PIN() and kwargs['scl'] == cls.SCL_PIN():
            if kwargs['frequency'] != 100000.0 and kwargs['frequency'] != 400000:
                raise ValueError(f"{cls} only supports 100kHz and 400kHz for "
                                 "the built in i2c controller")
