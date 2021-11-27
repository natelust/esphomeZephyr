from esphome.const import CONF_ID
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.core import CORE
from esphome.components.zephyr import add_Kconfig

DEPENDENCIES = ['openthread']

openthread_srp_ns = cg.esphome_ns.namespace("openthread_srp")
OpenThreadSRPComponent = openthread_srp_ns.class_("OpenThreadSRP",
                                                  cg.Component)


def _remove_id_if_disabled(value):
    value = value.copy()
    if value[CONF_DISABLED]:
        value.pop(CONF_ID)
    return value


def _zephyr_only(value):
    if not CORE.is_zephyr:
        raise cv.Invalid("OpenThreadSRP can only be used with Zephr")
    add_Kconfig("CONFIG_OPENTHREAD_SRP_CLIENT", "y")
    return value


CONF_DISABLED = "disabled"
CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(OpenThreadSRPComponent),
            cv.Optional(CONF_DISABLED, default=False): cv.boolean,
        }
    ),
    _remove_id_if_disabled,
    _zephyr_only
)


async def to_code(config):
    if config[CONF_DISABLED]:
        return
    cg.add_define("USE_OT_SRP")

    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
