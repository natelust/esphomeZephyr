from abc import ABC, abstractclassmethod
import textwrap

from typing import Tuple


class BaseZephyrBoard(ABC):
    @abstractclassmethod
    def validate_gpio_pin(cls, value):
        raise NotImplementedError("Not implemented on the base class")

    @abstractclassmethod
    def validate_supports(cls, value):
        raise NotImplementedError("Not implemented on the base class")

    @abstractclassmethod
    def get_device_and_pin(cls, pin):
        raise NotImplementedError("Not implemented on the base class")

    @abstractclassmethod
    def can_openthread(cls) -> bool:
        raise NotImplementedError("Not implemented on the base class")

    @abstractclassmethod
    def SDA_PIN(cls) -> str:
        raise NotImplementedError("Not implemented on the base class")

    @abstractclassmethod
    def SCL_PIN(cls) -> str:
        raise NotImplementedError("Not implemented on the base class")

    @abstractclassmethod
    def i2c_arg_validator(cls, **kwargs):
        raise NotImplementedError("Not implemented on the base class")

    @classmethod
    def handle_i2c(cls, **kwargs) -> Tuple[str, str, str]:
        from esphome.core import CORE
        if kwargs['sda'] == 'SDA':
            kwargs['sda'] = cls.SDA_PIN()
        if kwargs['scl'] == 'SCL':
            kwargs['scl'] = cls.SCL_PIN()
        cls.i2c_arg_validator(**kwargs)
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
            sda_controller, sda_pin = cls.get_device_and_pin(pin=kwargs['sda'])
            scl_controller, scl_pin = cls.get_device_and_pin(pin=kwargs['scl'])
            i2c_gpio_device = i2c_gpio_device.format(int(kwargs['frequency']),
                                                     sda_controller,
                                                     sda_pin,
                                                     scl_controller,
                                                     scl_pin)
            CORE.zephyr_manager.device_overlay_list.append(i2c_gpio_device)
            CORE.zephyr_manager.add_Kconfig("CONFIG_I2C_GPIO", "y")
            return ("gpioi2c0", kwargs['sda'], kwargs['scl'])
