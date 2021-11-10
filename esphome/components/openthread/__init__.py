from voluptuous.schema_builder import Required
from esphome.components.zephyr.const import KEY_BOARD, ZEPHYR_CORE_KEY, KCONFIG_KEY
from esphome.const import (KEY_CORE, KEY_TARGET_PLATFORM)

from esphome.core import CORE, EsphomeError
import esphome.config_validation as cv


CONF_NETWORK_NAME = "network_name"
CONF_NETWORK_CHANNEL = "network_channel"
CONF_NETWORK_KEY = "network_key"
CONF_PANID = "panID"
CONF_XPANID = "xpanID"


def set_core_data(config):
    cv.only_on_zephyr(config)
    Kconfigs = CORE.data[ZEPHYR_CORE_KEY][KCONFIG_KEY]
    Kconfigs['CONFIG_OPENTHREAD_CHANNEL'] = config[CONF_NETWORK_CHANNEL]
    Kconfigs['CONFIG_OPENTHREAD_NETWORK_NAME'] = config[CONF_NETWORK_NAME]
    Kconfigs['CONFIG_OPENTHREAD_XPANID'] = config[CONF_XPANID]
    Kconfigs['CONFIG_OPENTHREAD_PANID'] = config[CONF_PANID]
    Kconfigs['CONFIG_OPENTHREAD_JOINER'] = "y"
    Kconfigs['CONFIG_OPENTHREAD_JOINER_AUTOSTART'] = "y"
    Kconfigs["CONFIG_OPENTHREAD_VERSION_1_2"] = "y"
    Kconfigs["CONFIG_OPENTHREAD_COAP"] = "y"
    Kconfigs["CONFIG_OPENTHREAD_COAPs"] = "y"
    Kconfigs["CONFIG_OPENTHREAD_SRP_CLIENT"] = "y"
    Kconfigs["CONFIG_OPENTHREAD_SHELL"] = "y"

    Kconfigs['CONFIG_NET_L2_OPENTHREAD'] = "y"
    Kconfigs["CONFIG_NET_IPV4"] = "n"
    Kconfigs["CONFIG_NET_CONFIG_NEED_IPV4"] = "n"
    Kconfigs["CONFIG_SYSTEM_WORKQUEUE_STACK_SIZE"] = 2048


def _verify_network_key(value):
    value = cv.string_strict(value)
    for pair in value.split(':'):
        if len(pair) != 2:
            raise cv.Invalid("Does not appear to be valid network key")
    return value


OpenThreadComponent = object()


CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(OpenThreadComponent),
            cv.Required(CONF_NETWORK_NAME): cv.string_strict,
            cv.Required(CONF_NETWORK_CHANNEL): cv.int_,
            cv.Required(CONF_NETWORK_KEY): _verify_network_key,
            cv.Required(CONF_PANID): cv.int_,
            cv.Required(CONF_XPANID): cv.string_strict,

        }
    )
)