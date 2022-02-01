from __future__ import annotations
from abc import ABC, abstractmethod
import os
import textwrap
from time import sleep

from typing import List, Tuple, Mapping, TYPE_CHECKING
from ..zephyr_writer import ZephyrDirectoryBuilder

if TYPE_CHECKING:
    from esphome.components.zephyr.zephyrManager import ZephyrManager

from esphome.util import run_external_process


class BaseZephyrBoard(ABC):
    def __init__(self, manager: ZephyrManager, *args, **kwargs) -> None:
        super().__init__()
        self._manager = manager

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
    def i2c_arg_parser(self, kwargs):
        raise NotImplementedError("Not implemented on the base class")

    @abstractmethod
    def i2c_hardware_handler(self, device: str, kwargs):
        raise NotImplementedError("Not implemented on the base class")

    def handle_i2c(self, **kwargs) -> Tuple[str, str, str]:
        hardware, device = self.i2c_arg_parser(kwargs)
        if hardware:
            return self.i2c_hardware_handler(device, kwargs)
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
            self._manager.device_overlay_list.append(i2c_gpio_device)
            self._manager.add_Kconfig("CONFIG_I2C_GPIO", "y")
            return ("gpioi2c0", kwargs['sda'], kwargs['scl'])

    def flash_mapping(self) -> str:
        """DO NOT MODIFY THIS WITHOUT ALSO REFLASHING THE BOOTLOADER
        """
        return ""

    def pre_compile_bootloader(self, args: List[str]) -> List[str]:
        return args

    def pre_compile_application(self, args: List[str]) -> List[str]:
        return args

    @abstractmethod
    def spi_arg_parser(self, kwargs):
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
        self._manager.device_overlay_list.append(updated_spi_dev)
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

    def upload(self, flash_args: str, boot_dir: os.PathLike,
               proj_dir: os.PathLike, boot_info_path: os.PathLike,
               bootloader: bool, host: str):
        local_flash_args = ["west",
                            "flash",
                            "-d",
                            os.path.join(boot_dir, "build"),
                            ]
        # replace any placehonders for build_dir
        extra_args_str = flash_args
        extra_args_str = extra_args_str.replace("SERIAL_DEVICE", host)

        if not bootloader:
            boot_extra_args_str = extra_args_str.replace("BUILD_DIR", os.path.join(boot_dir, "build")).replace('.signed', '')
            boot_flash_args = local_flash_args + boot_extra_args_str.split()
            print("### FLASHING BOOTLOADER #####")
            result = run_external_process(*boot_flash_args)
            if result != 0:
                return result
            with open(boot_info_path, 'w') as f:
                f.write("")
            sleep(2)

        print("### FLASHING APPLICATION #####")
        local_flash_args[3] = os.path.join(proj_dir, "build")
        app_extra_args_str = extra_args_str.replace("BUILD_DIR", os.path.join(proj_dir, "build"))
        app_extra_args_str = app_extra_args_str.replace("zephyr.hex", "zephyr.signed.confirmed.hex")
        app_flash_args = local_flash_args + app_extra_args_str.split()
        print(f"Running {app_flash_args}")
        result = run_external_process(*app_flash_args)

        return result

    def get_writer(self) -> ZephyrDirectoryBuilder:
        return ZephyrDirectoryBuilder(self._manager)