import logging

from esphome.const import (
    CONF_ID,
    CONF_INPUT,
    CONF_INVERTED,
    CONF_MODE,
    CONF_NUMBER,
    CONF_OPEN_DRAIN,
    CONF_OUTPUT,
    CONF_PULLDOWN,
    CONF_PULLUP,
)

from esphome import pins
from esphome.core import CORE
import esphome.codegen as cg
import esphome.config_validation as cv

from .boards import registry
from .const import ZEPHYR_CORE_KEY, KEY_BOARD, zephyr_ns

_LOGGER = logging.getLogger(__name__)


ZephyrGPIOPin = zephyr_ns.class_("ZephyrGPIOPin", cg.InternalGPIOPin)


def validate_gpio_pin(value):
    if CORE.zephyr_manager is not None:
        return CORE.zephyr_manager.board.validate_gpio_pin(value)
    else:
        raise cv.Invalid("Cannot validate board GPIO")


def validate_supports(value):
    if CORE.zephyr_manager is not None:
        return CORE.zephyr_manager.board.validate_supports(value)
    else:
        raise cv.Invalid("Cannot validate board GPIO")


CONF_ANALOG = "analog"
ZEPHYR_PIN_SCHEMA = cv.All(
    {
        cv.GenerateID(): cv.declare_id(ZephyrGPIOPin),
        cv.Required(CONF_NUMBER): validate_gpio_pin,
        cv.Optional(CONF_MODE, default={}): cv.Schema(
            {
                cv.Optional(CONF_ANALOG, default=False): cv.boolean,
                cv.Optional(CONF_INPUT, default=False): cv.boolean,
                cv.Optional(CONF_OUTPUT, default=False): cv.boolean,
                cv.Optional(CONF_OPEN_DRAIN, default=False): cv.boolean,
                cv.Optional(CONF_PULLUP, default=False): cv.boolean,
                cv.Optional(CONF_PULLDOWN, default=False): cv.boolean,
            }
        ),
        cv.Optional(CONF_INVERTED, default=False): cv.boolean,
    },
    lambda x: x
)


@pins.PIN_SCHEMA_REGISTRY.register("zephyr", ZEPHYR_PIN_SCHEMA)
async def zephyr_pin_to_code(config):
    CORE.zephyr_manager.add_Kconfig("CONFIG_GPIO", "y")
    var = cg.new_Pvariable(config[CONF_ID])
    num = config[CONF_NUMBER]
    assert CORE.zephyr_manager is not None
    gpio_port, gpio_pin = CORE.zephyr_manager.board.get_device_and_pin(num)
    cg.add(var.set_device_label(cg.RawExpression(f"DT_LABEL(DT_NODELABEL({gpio_port}))")))
    cg.add(var.set_pin(gpio_pin))
    cg.add(var.set_inverted(config[CONF_INVERTED]))
    cg.add(var.set_flags(pins.gpio_flags_expr(config[CONF_MODE])))
    return var
