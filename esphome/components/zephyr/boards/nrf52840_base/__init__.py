from abc import abstractmethod
import textwrap
from typing import Tuple, Mapping

from ..baseBoard import BaseZephyrBoard
from .. import registry

import esphome.config_validation as cv

GPIO_0 = "gpio0"
GPIO_1 = "gpio1"


class NRF52840Base(BaseZephyrBoard):
    def __init__(self, mangager, *args, **kwargs) -> None:
        super().__init__(mangager)
        self.hardware_i2c_devices = ["i2c0"]

    @property
    @abstractmethod
    def pinMapping(self) -> Mapping[str, Tuple[str, int]]:
        raise NotImplementedError("Not implemented on the base class")

    @property
    @abstractmethod
    def analogMapping(self) -> Mapping[str, int]:
        raise NotImplementedError("Not implemented on the base class")

    @abstractmethod
    def __str__(self):
        raise NotImplementedError("Not implemented on the base class")

    def validate_gpio_pin(self, value):
        # do nothing for now, fix this later
        return value

    def validate_supports(self, value):
        # do nothing for now, fix this later
        return value

    def get_device_and_pin(self, pin):
        value = self.pinMapping.get(pin)
        if value is None:
            raise NotImplementedError(f"Cannot handle pin specifier {pin}, "
                                      f"must be one of {self.pinMapping.keys()}")
        return value

    def can_openthread(self) -> bool:
        return True

    def i2c_arg_parser(self, kwargs):
        if self.hardware_i2c_devices:
            hardware = True
            device = self.hardware_i2c_devices.pop()
        else:
            hardware = False
            device = "gpioi2c0"

        if hardware is True:
            if kwargs['frequency'] != 100000.0 and kwargs['frequency'] != 400000:
                raise ValueError(f"{type(self)} only supports 100kHz and 400kHz for "
                                    "the built in i2c controller")
        return hardware, device

    def i2c_hardware_handler(self, device: str, kwargs):
        updated_i2c_dev = textwrap.dedent("""
        &{} {{
            clock-frequency = < {} >;
            sda-pin = < {} >;
            scl-pin = < {} >;
            status =  "ok" ;
        }};
        """)
        sda_controller, sda_pin = self.get_device_and_pin(pin=kwargs['sda'])
        if sda_controller == GPIO_1:
            sda_pin += 32
        scl_controller, scl_pin = self.get_device_and_pin(pin=kwargs['scl'])
        if scl_controller == GPIO_1:
            scl_pin += 32

        updated_i2c_dev = updated_i2c_dev.format(device, int(kwargs['frequency']),
                                                    sda_pin, scl_pin)
        self._manager.device_overlay_list.append(updated_i2c_dev)
        return (device, kwargs['sda'], kwargs['scl'])

    def spi_device(self) -> str:
        return "spi1"

    def spi_arg_parser(self, kwargs):
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
        return self.analogMapping[pin]

    def adc_device(self) -> str:
        return "adc"

    def validate_adc_pin(self, value):
        in_pin = value
        if in_pin not in self.analogMapping:
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
