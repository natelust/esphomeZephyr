from esphome.components.zephyr.const import KEY_BOARD
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
                    ZEPHYR_BASE, zephyr_ns, KCONFIG_KEY)


def set_core_data(config):
    CORE.data[ZEPHYR_CORE_KEY] = {}
    CORE.data[KEY_CORE][KEY_TARGET_PLATFORM] = "zephyr"
    CORE.data[KEY_CORE][KEY_TARGET_FRAMEWORK] = "zephyr"
    if config.get(CONF_FRAMEWORK) is not None:
        version = config[CONF_FRAMEWORK][CONF_VERSION]
    else:
        version = ZEPHYR_FRAMEWORK_DEFUALT_VERSION
    CORE.data[KEY_CORE][KEY_FRAMEWORK_VERSION] = version
    CORE.data[ZEPHYR_CORE_KEY][KEY_BOARD] = config[CONF_BOARD]
    CORE.data[ZEPHYR_CORE_KEY][ZEPHYR_BASE] = config[ZEPHYR_BASE]
    CORE.data[ZEPHYR_CORE_KEY][KCONFIG_KEY] = config[KCONFIG_KEY]
    Kconfigs = CORE.data[ZEPHYR_CORE_KEY][KCONFIG_KEY]
    Kconfigs["CONFIG_CPLUSPLUS"] = "Y"
    Kconfigs["CONFIG_NEWLIB_LIBC"] = "y"
    Kconfigs["CONFIG_LLIB_CPLUSPLUS"] = "y"
    Kconfigs["CONFIG_STD_CPP14"] = "y"

    return config


def _zephyr_check_versions(value):
    if value != value[CONF_VERSION][0:3] != "2.6":
        raise cv.Invalid("Can only handle zephyr version 2.6.X")


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
            cv.Optional(KCONFIG_KEY, default=[]): cv.Any(dict)
        }
    ),
    set_core_data
)


@coroutine_with_priority(1000)
async def to_code(config):
    cg.add_global(cg.RawStatement("#include <zephyr.h>"))
