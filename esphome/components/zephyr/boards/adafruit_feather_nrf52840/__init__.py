from typing import Tuple, Mapping

from ..baseBoardValidator import BaseZephyrBoard
from .. import registry

import esphome.config_validation as cv

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
class AdafruitFeatherNrf52840(BaseZephyrBoard):
    def __str__(self):
        return "adafruit_feather_nrf52840"

    def SDA_PIN(self) -> str:
        return "D22"

    def SCL_PIN(self) -> str:
        return "D23"

    def validate_gpio_pin(self, value):
        # do nothing for now, fix this later
        return value

    def validate_supports(self, value):
        # do nothing for now, fix this later
        return value

    def get_device_and_pin(self, pin):
        value = pinMapping.get(pin)
        if value is None:
            raise NotImplementedError(f"Cannot handle pin specifier {pin}, "
                                      f"must be one of {pinMapping.keys()}")
        return value

    def can_openthread(self) -> bool:
        return True

    def i2c_arg_validator(self, **kwargs):
        if kwargs['sda'] == self.SDA_PIN() and kwargs['scl'] == self.SCL_PIN():
            if kwargs['frequency'] != 100000.0 and kwargs['frequency'] != 400000:
                raise ValueError(f"{type(self)} only supports 100kHz and 400kHz for "
                                 "the built in i2c controller")

    def spi_device(self) -> str:
        return "spi1"

    def spi_arg_validator(self, **kwargs):
        return

    def spi_pins(self, clk=None, mosi=None, miso=None) -> Mapping[str, str]:
        if clk is None:
            clk = "D26"
        if mosi is None:
            mosi = "D25"
        if miso is None:
            miso = "D24"
        result = {}
        for name, pointer in (("clk", clk), ("mosi", mosi), ("miso", miso)):
            controller, pin = self.get_device_and_pin(pointer)
            if controller == GPIO_1:
                pin += 32
            result[name] = pin
        return result

    def get_analog_channel(self, pin) -> int:
        return analogMapping[pin]

    def adc_device(self) -> str:
        return "adc"

    def validate_adc_pin(self, value):
        in_pin = value
        if in_pin not in  ("A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7",
                           "D14", "D15", "D16", "D17", "D18", "D19", "D20",
                           "D21"):
            raise cv.Invalid(f"{value} cannot be used as ADC on {self}")
        pin = self.get_analog_channel(in_pin)
        return pin

    def adc_arg_validator(self, **kwargs) -> None:
        #if kwargs['gain'].enum_value not in ("ADC_GAIN_1_3", "ADC_GAIN_2_3",
                                             #"ADC_GAIN_1"):
            #raise cv.Invalid(f"{self} does not support gain {kwargs['gain']}")
        if kwargs['ref'].enum_value not in ("ADC_REF_INTERNAL",
                                            "ADC_REF_VDD_1_2",
                                            "ADC_REF_VDD_1_3",
                                            "ADC_REF_VDD_1_4",
                                            "ADC_REF_EXTERNAL0",
                                            "ADC_REF_EXTERNAL1"):
            raise cv.Invalid(f"{self} does not support reference "
                             f"{kwargs['ref']}")
