from abc import ABC, abstractmethod
import textwrap

from typing import Tuple, Mapping


class BaseZephyrBoard(ABC):
    @abstractmethod
    def validate_gpio_pin(self, value):
        raise NotImplementedError("Not implemented on the base class")

    @abstractmethod
    def validate_supports(self, value):
        raise NotImplementedError("Not implemented on the base class")

    @abstractmethod
    def validate_adc_pin(self, value):
        raise NotImplementedError("Not implemented on the base class")

    @abstractmethod
    def get_device_and_pin(self, pin):
        raise NotImplementedError("Not implemented on the base class")

    @abstractmethod
    def can_openthread(self) -> bool:
        raise NotImplementedError("Not implemented on the base class")

    @abstractmethod
    def SDA_PIN(self) -> str:
        raise NotImplementedError("Not implemented on the base class")

    @abstractmethod
    def SCL_PIN(self) -> str:
        raise NotImplementedError("Not implemented on the base class")

    @abstractmethod
    def i2c_arg_validator(self, **kwargs):
        raise NotImplementedError("Not implemented on the base class")

    def handle_i2c(self, **kwargs) -> Tuple[str, str, str]:
        from esphome.core import CORE
        if kwargs['sda'] == 'SDA':
            kwargs['sda'] = self.SDA_PIN()
        if kwargs['scl'] == 'SCL':
            kwargs['scl'] = self.SCL_PIN()
        self.i2c_arg_validator(**kwargs)
        if kwargs['sda'] == "D22" and kwargs['scl'] == "D23":
            updated_i2c_dev = textwrap.dedent("""
            &i2c0 {{
                clock-frequency = < {} >;
            }};
            """)
            updated_i2c_dev = updated_i2c_dev.format(int(kwargs['frequency']))
            CORE.zephyr_manager.device_overlay_list.append(updated_i2c_dev)
            return ("i2c0", kwargs['sda'], kwargs['scl'])
        else:
            i2c_gpio_device = textwrap.dedent("""
            / {{
                    gpioi2c0: gpio_i2c {{
                        compatible = "gpio-i2c";
                        status = "okay";
                        clock-frequency = < {} >;
                        sda-gpios = <&{} {} (GPIO_OPEN_DRAIN)>;
                        scl-gpios = <&{} {} (GPIO_OPEN_DRAIN)>;
                        label = "GPIOI2C_0";
                        #address-cells = <1>;
                        #size-cells = <0>;
                    }};
              }};""")
            sda_controller, sda_pin = self.get_device_and_pin(pin=kwargs['sda'])
            scl_controller, scl_pin = self.get_device_and_pin(pin=kwargs['scl'])
            i2c_gpio_device = i2c_gpio_device.format(int(kwargs['frequency']),
                                                     sda_controller,
                                                     sda_pin,
                                                     scl_controller,
                                                     scl_pin)
            CORE.zephyr_manager.device_overlay_list.append(i2c_gpio_device)
            CORE.zephyr_manager.add_Kconfig("CONFIG_I2C_GPIO", "y")
            return ("gpioi2c0", kwargs['sda'], kwargs['scl'])

    @abstractmethod
    def spi_arg_validator(self, **kwargs):
        raise NotImplementedError("Not implemented on the base class")

    @abstractmethod
    def spi_device(self) -> str:
        raise NotImplementedError("Not implemented on the base class")

    @abstractmethod
    def spi_pins(self, clk=None, mosi=None, miso=None) -> Mapping[str, str]:
        """This must return a mapping with keys clk, mosi, miso corresponding
        to strings of the corresponding pins.
        """
        raise NotImplementedError("Not implemented on the base class")

    def handle_spi(self, **kwargs) -> Mapping[str, str]:
        from esphome.core import CORE
        clk_pin = kwargs.get("clk_pin")
        mosi_pin = kwargs.get("mosi_pin")
        miso_pin = kwargs.get("miso_pin")
        pins = self.spi_pins(clk = clk_pin['number'] if clk_pin is not None else None,
                             mosi = mosi_pin['number'] if mosi_pin is not None else None,
                             miso = miso_pin['number'] if miso_pin is not None else None)

        updated_spi_dev = textwrap.dedent("""
        &{device}  {{
          sck-pin = < {sck} >;
          mosi-pin = < {mosi} >;
          miso-pin = < {miso} >;
        }};
        """)
        updated_spi_dev = updated_spi_dev.format(device=self.spi_device(),
                                                 sck=pins['clk'],
                                                 mosi=pins['mosi'],
                                                 miso=pins['miso'])
        CORE.zephyr_manager.device_overlay_list.append(updated_spi_dev)
        result = dict(pins.items())
        result['device'] = self.spi_device()
        return result

    @abstractmethod
    def adc_arg_validator(self, **kwargs) -> None:
        raise NotImplementedError("Not implemented on the base class")

    @abstractmethod
    def adc_device(self) -> str:
        raise NotImplementedError("Not implemented on the base class")

    @abstractmethod
    def get_analog_channel(self, pin) -> int:
        raise NotImplementedError("Not implemented on the base class")

    def handle_adc(self, **kwargs) -> Tuple[str, int]:
        self.adc_arg_validator(**kwargs)
        pin = self.get_analog_channel(kwargs['pin'])
        return self.adc_device(), pin