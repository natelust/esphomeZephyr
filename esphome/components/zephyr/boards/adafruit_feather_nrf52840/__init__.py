from ..baseBoardValidator import BaseBoardBValidator
from .. import registry

GPIO_0 = "DT_ALIAS_GPIO_0_LABEL"
GPIO_1 = "DT_ALIAS_GPIO_1_LABEL"

pinMapping = {
    "D0": (GPIO_0, 25),
    "D1": (GPIO_0, 24),
    "D2": (GPIO_0, 10),
    "D3": (GPIO_1, 15),
    "D4": (GPIO_1, 10),
    "D5": (GPIO_1, 8),
    "D6": (GPIO_0, 7),
    "D7": (GPIO_1, 2),
    "D8": (GPIO_0, 16),
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
    "D20": (GPIO_0, 29),
    "D21": (GPIO_0, 31),
    "A0": (GPIO_0, 4),
    "A1": (GPIO_0, 5),
    "A2": (GPIO_0, 30),
    "A3": (GPIO_0, 28),
    "A4": (GPIO_0, 2),
    "A5": (GPIO_0, 3),
    "A6": (GPIO_0, 29),
    "A7": (GPIO_0, 31),
    "D22": (GPIO_0, 12),
    "D23": (GPIO_0, 11),
    "D24": (GPIO_0, 15),
    "D25": (GPIO_0, 13),
    "D26": (GPIO_0, 14),
    "D27": (GPIO_0, 19),
    "D28": (GPIO_0, 20),
    "D29": (GPIO_0, 17),
    "D30": (GPIO_0, 22),
    "D31": (GPIO_0, 23),
    "D32": (GPIO_0, 21),
    "D33": (GPIO_0, 9)
}


@registry.register("adafruit_feather_nrf52840")
class AdafruitFeatherNrf52840(BaseBoardBValidator):
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
