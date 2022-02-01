from datetime import datetime

from esphome.const import (
    CONF_BOARD,
    CONF_FRAMEWORK,
    CONF_VERSION,
    KEY_CORE,
    KEY_FRAMEWORK_VERSION,
    KEY_TARGET_FRAMEWORK,
    KEY_TARGET_PLATFORM
)

from esphome.core import CORE, coroutine_with_priority
import esphome.config_validation as cv
import esphome.codegen as cg

from .gpio import zephyr_pin_to_code  # noqa
from .const import (ZEPHYR_CORE_KEY, ZEPHYR_FRAMEWORK_DEFUALT_VERSION,
                    ZEPHYR_BASE, KCONFIG_KEY, FLASH_ARGS)

from .zephyrManager import ZephyrManager


def set_core_data(config):
    CORE.data[ZEPHYR_CORE_KEY] = {}
    CORE.data[KEY_CORE][KEY_TARGET_PLATFORM] = "zephyr"
    CORE.data[KEY_CORE][KEY_TARGET_FRAMEWORK] = "zephyr"
    if config.get(CONF_FRAMEWORK) is not None:
        version = config[CONF_FRAMEWORK][CONF_VERSION]
    else:
        version = ZEPHYR_FRAMEWORK_DEFUALT_VERSION
    CORE.data[KEY_CORE][KEY_FRAMEWORK_VERSION] = version

    manager = CORE.data[ZEPHYR_CORE_KEY] = ZephyrManager(config[CONF_BOARD],
                                                         config[ZEPHYR_BASE],
                                                         config[KCONFIG_KEY],
                                                         config[FLASH_ARGS])

    now = datetime.now()
    version = f"{now.year-2000}.{now.month}.{now.day}+{now.hour if now.hour !=0 else ''}{now.minute:02d}{now.second:02d}"
    manager.add_Kconfig_vec((
        ("CONFIG_CPLUSPLUS", "y"),
        ("CONFIG_NEWLIB_LIBC", "y"),
        ("CONFIG_LIB_CPLUSPLUS", "y"),
        ("CONFIG_STD_CPP14", "y"),
        ("CONFIG_HARDWARE_DEVICE_CS_GENERATOR", "y"),
        ("CONFIG_ENTROPY_DEVICE_RANDOM_GENERATOR", "y"),
        ("CONFIG_REBOOT", "y"),
        #("CONFIG_USB", "y"),
        ("CONFIG_SHELL", "y"),
        ("CONFIG_CONSOLE", "y"),
        #("CONFIG_USB_UART_CONSOLE", "y"),
        ("CONFIG_UART_INTERRUPT_DRIVEN", "y"),
        ("CONFIG_SYSTEM_WORKQUEUE_STACK_SIZE", 2048),
        ("CONFIG_MAIN_STACK_SIZE", 3072),
        #("CONFIG_CONSOLE_SHELL", 'y'),
    #('CONFIG_SHELL_BACKEND_SERIAL', 'y'),
        #('CONFIG_THREAD_MONITOR', 'y'),
        #('CONFIG_THREAD_NAME', 'y'),
        #('CONFIG_LOG_BUFFER_SIZE', 32768),
        ('CONFIG_LOG_STRDUP_BUF_COUNT', 300),
        ('CONFIG_LOG_STRDUP_MAX_STRING', 100),
        #('CONFIG_UART_CONSOLE_INIT_PRIORITY', 95),
        ('CONFIG_FPU', 'y'),
    #Kconfigs["CONFIG_UART_CONSOLE_ON_DEV_NAME"] = '"CDC_ACM_0"'
        ("CONFIG_SERIAL", "y"),
        ("CONFIG_UART_LINE_CTRL", "y"),
        ("CONFIG_USB_DEVICE_STACK", "y"),
        ("CONFIG_USB_DEVICE_PRODUCT", f'"{CORE.name} USB Device"'),
        ("CONFIG_USB_CDC_ACM", "y"),
        ("CONFIG_USB_REQUEST_BUFFER_SIZE", 2048),
        ("CONFIG_USB_CDC_ACM_RINGBUF_SIZE", 2048),
        ('CONFIG_INIT_STACKS', 'y'),
        ('CONFIG_STDOUT_CONSOLE', 'y'),
        ('CONFIG_SHELL_STACK_SIZE', 4096),
        ('CONFIG_SHELL_BACKEND_SERIAL_INIT_PRIORITY', 51),
        ('CONFIG_SHELL_TAB', "y"),
        ('CONFIG_SHELL_TAB_AUTOCOMPLETION', "y"),
        ('CONFIG_SHELL_METAKEYS', "n"),
        ("CONFIG_NET_BUF_USER_DATA_SIZE", 24),
        ("CONFIG_SHELL_MINIMAL", "y"),
        ("CONFIG_DEBUG", "n"),
        ("CONFIG_BOOT_BANNER", "n"),
        ("CONFIG_MCUMGR", "y"),
        ("CONFIG_MCUMGR_CMD_IMG_MGMT", "y"),
        ("CONFIG_MCUMGR_CMD_OS_MGMT", "y"),
        ("CONFIG_SYSTEM_WORKQUEUE_STACK_SIZE", 2304),
        ("CONFIG_MCUMGR_SMP_UDP_IPV6", "y"),
        ("CONFIG_MCUMGR_SMP_UDP", "y"),
        #("CONFIG_MCUMGR_SMP_UDP_STACK_SIZE", 768),
        #("CONFIG_MCUMGR_BUF_USER_DATA_SIZE", 40),
        #("CONFIG_MCUMGR_BUF_COUNT", 10),
        ("CONFIG_MCUBOOT_EXTRA_IMGTOOL_ARGS", f'"--version {version}"'),
        #("CONFIG_MCUMGR_SMP_SHELL", "y"),
        ("CONFIG_MBEDTLS_AES_ROM_TABLES", "n"),
        #("CONFIG_MCUMGR_SMP_UDP_IPV4", "y"),
    ))


        #("CONFIG_KERNEL_SHELL", 'y'),
        #('CONFIG_DEVICE_SHELL', 'y'),
    #CORE.data[ZEPHYR_CORE_KEY][KEY_BOARD] = config[CONF_BOARD]
    #CORE.data[ZEPHYR_CORE_KEY][ZEPHYR_BASE] = config[ZEPHYR_BASE]
    #CORE.data[ZEPHYR_CORE_KEY][KCONFIG_KEY] = config[KCONFIG_KEY]
    #Kconfigs = CORE.data[ZEPHYR_CORE_KEY][KCONFIG_KEY]
    #Kconfigs["CONFIG_CPLUSPLUS"] = "y"
    #Kconfigs["CONFIG_NEWLIB_LIBC"] = "y"
    #Kconfigs["CONFIG_LIB_CPLUSPLUS"] = "y"
    #Kconfigs["CONFIG_STD_CPP14"] = "y"
    #Kconfigs["CONFIG_HARDWARE_DEVICE_CS_GENERATOR"] = "y"
    #Kconfigs["CONFIG_ENTROPY_DEVICE_RANDOM_GENERATOR"] = "y"
    #Kconfigs['CONFIG_TIMER_RANDOM_GENERATOR'] = "y"
    #Kconfigs["CONFIG_REBOOT"] = "y"

    #Kconfigs["CONFIG_USB"] = "y"
    #Kconfigs["CONFIG_USB_UART_CONSOLE"] = "y"
    #Kconfigs["CONFIG_UART_INTERRUPT_DRIVEN"] = "y"
    #Kconfigs["CONFIG_SYSTEM_WORKQUEUE_STACK_SIZE"] = 2048
    #Kconfigs["CONFIG_MAIN_STACK_SIZE"] = 3072

    #Kconfigs["CONFIG_CONSOLE_SHELL"] = 'y'

    #Kconfigs['CONFIG_SHELL_MINIMAL'] = 'y'
    #Kconfigs['CONFIG_SHELL_BACKEND_SERIAL'] = 'y'
    #Kconfigs['CONFIG_THREAD_MONITOR'] = 'y'
    #Kconfigs['CONFIG_THREAD_NAME'] = 'y'
    #Kconfigs['CONFIG_CBPRINTF_NANO'] = 'y'
    #Kconfigs['CONFIG_LOG_BUFFER_SIZE'] = 32768
    #Kconfigs['CONFIG_KERNEL_LOG_LEVEL_DBG'] = "y"
    #Kconfigs['CONFIG_LOG_STRDUP_BUF_COUNT'] = 300
    #Kconfigs['CONFIG_LOG_STRDUP_MAX_STRING'] = 100
    #Kconfigs['CONFIG_UART_CONSOLE_INIT_PRIORITY'] = 95
    #Kconfigs['CONFIG_FPU'] = 'y'
    #Kconfigs['CONFIG_NO_OPTIMIZATIONS'] = 'y'
    #Kconfigs['CONFIG_MBEDTLS_SHA1_C'] = 'n'

    #Kconfigs["CONFIG_UART_CONSOLE_ON_DEV_NAME"] = '"CDC_ACM_0"'

    # new commented
    #Kconfigs["CONFIG_SERIAL"] = "y"
    #Kconfigs["CONFIG_UART_LINE_CTRL"] = "y"
    #Kconfigs["CONFIG_USB_DEVICE_STACK"] = "y"
    #Kconfigs["CONFIG_USB_DEVICE_PRODUCT"] = '"MINE Zephyr USB console sample"'
    #Kconfigs["CONFIG_USB_CDC_ACM"] = "y"
    #Kconfigs["CONFIG_USB_REQUEST_BUFFER_SIZE"] = 2048
    #Kconfigs["CONFIG_USB_CDC_ACM_RINGBUF_SIZE"] = 2048

    #Kconfigs["CONFIG_KERNEL_SHELL"] = 'y'
    #Kconfigs['CONFIG_INIT_STACKS'] = 'y'
    #Kconfigs['CONFIG_STDOUT_CONSOLE'] = 'y'
    #Kconfigs['CONFIG_DEVICE_SHELL'] = 'y'
    #Kconfigs['CONFIG_SHELL_STACK_SIZE'] = 4096
    #Kconfigs['CONFIG_SHELL_BACKEND_SERIAL_INIT_PRIORITY'] = 51
    #Kconfigs['CONFIG_SHELL_TAB'] = "y"
    #Kconfigs['CONFIG_SHELL_TAB_AUTOCOMPLETION'] = "y"
    #Kconfigs['CONFIG_SHELL_METAKEYS'] = "y"


    return config


def _zephyr_check_versions(value):
    if value != value[CONF_VERSION][0:3] != "2.6":
        raise cv.Invalid("Can only handle zephyr version 2.6.X")
    return value


ZEPHYR_FRAMEWORK_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.Optional(CONF_VERSION, default=ZEPHYR_FRAMEWORK_DEFUALT_VERSION): cv.string_strict
        }
    ),
    _zephyr_check_versions
)


CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.Required(CONF_BOARD): cv.string_strict,
            cv.Required(ZEPHYR_BASE): cv.string_strict,
            cv.Optional(CONF_FRAMEWORK, default={}): ZEPHYR_FRAMEWORK_SCHEMA,
            cv.Optional(KCONFIG_KEY, default={}): cv.Any(dict),
            cv.Required(FLASH_ARGS): cv.string_strict
        }
    ),
    set_core_data
)


@coroutine_with_priority(1000)
async def to_code(config):
    cg.add_global(cg.RawStatement("#include <zephyr.h>"))
    cg.add_global(cg.RawStatement("#include <sys/printk.h>"))
    cg.add_global(cg.RawStatement("#include <usb/usb_device.h>"))
    cg.add_global(cg.RawStatement("#include <sys/util.h>"))
    cg.add_global(cg.RawStatement("#include <drivers/uart.h>"))
    cg.add_define("ESPHOME_BOARD", "Zephyr")

    cg.add_define("USE_ZEPHYR")
