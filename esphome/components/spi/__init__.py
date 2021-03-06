import esphome.codegen as cg
import esphome.config_validation as cv
import esphome.final_validate as fv
from esphome import pins
from esphome.const import (
    CONF_CLK_PIN,
    CONF_ID,
    CONF_MISO_PIN,
    CONF_MOSI_PIN,
    CONF_SPI_ID,
    CONF_CS_PIN,
)
from esphome.core import coroutine_with_priority, CORE

CODEOWNERS = ["@esphome/core"]
spi_ns = cg.esphome_ns.namespace("spi")
SPIComponent = spi_ns.class_("SPIComponent", cg.Component)
#ESPSPIComponent = spi_ns.class_("ESPSPIComponent", cg.Component)
#ZephyrSPIComponent = spi_ns.class_("ZephyrSPIComponent", cg.Component)
SPIDevice = spi_ns.class_("SPIDevice")
MULTI_CONF = True


"""
def _bus_declare_type(value):
    if CORE.is_zephyr:
        return cv.declare_id(ZephyrSPIComponent)(value)
    else:
        return cv.declare_id(ESPSPIComponent)(value)
"""

CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(SPIComponent),
            cv.Required(CONF_CLK_PIN): pins.gpio_output_pin_schema,
            cv.Optional(CONF_MISO_PIN): pins.gpio_input_pin_schema,
            cv.Optional(CONF_MOSI_PIN): pins.gpio_output_pin_schema,
        }
    ),
    cv.has_at_least_one_key(CONF_MISO_PIN, CONF_MOSI_PIN),
)


@coroutine_with_priority(1.0)
async def to_code(config):
    cg.add_global(spi_ns.using)
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    if not CORE.is_zephyr:
        clk = await cg.gpio_pin_expression(config[CONF_CLK_PIN])
        cg.add(var.set_clk(clk))
        if CONF_MISO_PIN in config:
            miso = await cg.gpio_pin_expression(config[CONF_MISO_PIN])
            cg.add(var.set_miso(miso))
        if CONF_MOSI_PIN in config:
            mosi = await cg.gpio_pin_expression(config[CONF_MOSI_PIN])
            cg.add(var.set_mosi(mosi))

    if CORE.is_esp32:
        cg.add_library("SPI", None)

    if CORE.is_zephyr:
        result = CORE.zephyr_manager.handle_spi(**config)
        cg.add(var.set_miso_name("'{}'".format(result['miso'])))
        cg.add(var.set_mosi_name("'{}'".format(result['mosi'])))
        cg.add(var.set_clk_name("'{}'".format(result['clk'])))
        cg.add(var.set_device(cg.RawExpression(f'DT_LABEL(DT_NODELABEL({result["device"]}))')))


"""
def _id_selector():
    if CORE.is_zephyr:
        return cv.use_id(ZephyrSPIComponent)
    else:
        return cv.use_id(ESPSPIComponent)
"""

def spi_device_schema(cs_pin_required=True):
    """Create a schema for an SPI device.
    :param cs_pin_required: If true, make the CS_PIN required in the config.
    :return: The SPI device schema, `extend` this in your config schema.
    """
    schema = {
        cv.GenerateID(CONF_SPI_ID): cv.use_id(SPIComponent),
    }
    if cs_pin_required:
        schema[cv.Required(CONF_CS_PIN)] = pins.gpio_output_pin_schema
    else:
        schema[cv.Optional(CONF_CS_PIN)] = pins.gpio_output_pin_schema
    return cv.Schema(schema)


async def register_spi_device(var, config):
    parent = await cg.get_variable(config[CONF_SPI_ID])
    cg.add(var.set_spi_parent(parent))
    if CONF_CS_PIN in config:
        pin = await cg.gpio_pin_expression(config[CONF_CS_PIN])
        cg.add(var.set_cs_pin(pin))


def final_validate_device_schema(name: str, *, require_mosi: bool, require_miso: bool):
    hub_schema = {}
    if require_miso:
        hub_schema[
            cv.Required(
                CONF_MISO_PIN,
                msg=f"Component {name} requires this spi bus to declare a miso_pin",
            )
        ] = cv.valid
    if require_mosi:
        hub_schema[
            cv.Required(
                CONF_MOSI_PIN,
                msg=f"Component {name} requires this spi bus to declare a mosi_pin",
            )
        ] = cv.valid

    return cv.Schema(
        {cv.Required(CONF_SPI_ID): fv.id_declaration_match_schema(hub_schema)},
        extra=cv.ALLOW_EXTRA,
    )
