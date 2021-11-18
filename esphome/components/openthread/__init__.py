from voluptuous.schema_builder import Required
from esphome.components.zephyr import add_Kconfig
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
    add_Kconfig('CONFIG_NETWORKING', "y")
    add_Kconfig('CONFIG_OPENTHREAD_CHANNEL', config[CONF_NETWORK_CHANNEL])
    add_Kconfig('CONFIG_OPENTHREAD_NETWORK_NAME', f'"{config[CONF_NETWORK_NAME]}"')
    add_Kconfig('CONFIG_OPENTHREAD_XPANID', f'"{config[CONF_XPANID]}"')
    add_Kconfig('CONFIG_OPENTHREAD_PANID', config[CONF_PANID])
    add_Kconfig("CONFIG_OPENTHREAD_NETWORKKEY", f'"{config[CONF_NETWORK_KEY]}"')
    #add_Kconfig('CONFIG_OPENTHREAD_JOINER', "y")
    #add_Kconfig('CONFIG_OPENTHREAD_JOINER_AUTOSTART', "y")
    #add_Kconfig("CONFIG_OPENTHREAD_THREAD_VERSION_1_2", "y")
    add_Kconfig("CONFIG_OPENTHREAD_COAP", "y")
    #add_Kconfig("CONFIG_OPENTHREAD_COAPS", "y")
    #add_Kconfig("CONFIG_OPENTHREAD_SRP_CLIENT", "y")
    add_Kconfig("CONFIG_OPENTHREAD_SHELL", "y")
    #add_Kconfig("CONFIG_SHELL_STACK_SIZE", 3072)
    add_Kconfig("CONFIG_SHELL_ARGC_MAX", 26)
    add_Kconfig("CONFIG_SHELL_CMD_BUFF_SIZE", 416)
    add_Kconfig("CONFIG_NET_IPV4", "n")
    add_Kconfig("CONFIG_NET_IPV6", "y")
    add_Kconfig("CONFIG_NET_UDP", "y")
    add_Kconfig("CONFIG_NET_TCP", "y")
    add_Kconfig("CONFIG_NET_SOCKETS", "y")
    #add_Kconfig("CONFIG_NET_CONNECTION_MANAGER", "y")
    add_Kconfig("CONFIG_NET_CONFIG_SETTINGS", "y")
    add_Kconfig("CONFIG_SETTINGS_RUNTIME", "y")
    add_Kconfig("CONFIG_NET_SOCKETS_POSIX_NAMES", "y")
    add_Kconfig("CONFIG_NET_SOCKETS_POLL_MAX", 4)
    add_Kconfig("CONFIG_NET_SHELL", "y")
    add_Kconfig("CONFIG_NET_CONFIG_NEED_IPV6", "y")
    add_Kconfig("CONFIG_NET_IF_UNICAST_IPV6_ADDR_COUNT", 6)
    add_Kconfig("CONFIG_NET_IF_MCAST_IPV6_ADDR_COUNT", 8)

    add_Kconfig("CONFIG_NVS", "y")
    add_Kconfig("CONFIG_SETTINGS_NVS", "y")
    add_Kconfig("CONFIG_ARM_MPU", "n")

    add_Kconfig("CONFIG_OPENTHREAD_DEBUG", "y")
    add_Kconfig("CONFIG_OPENTHREAD_L2_DEBUG", "y")
    add_Kconfig("CONFIG_OPENTHREAD_L2_LOG_LEVEL_DBG", "y")
    #add_Kconfig("CONFIG_MBEDTLS_SSL_MAX_CONTENT_LEN", 768)

    add_Kconfig('CONFIG_NET_L2_OPENTHREAD', "y")
    #add_Kconfig('CONFIG_INIT_ARCH_HW_AT_BOOT', "y")
    add_Kconfig("CONFIG_OPENTHREAD_THREAD_STACK_SIZE", 6144)
    #add_Kconfig("CONFIG_NET_IPV4", "n")
    #add_Kconfig("CONFIG_NET_CONFIG_NEED_IPV4", "n")
    add_Kconfig('CONFIG_MBEDTLS_HEAP_SIZE', 10240)
    add_Kconfig("CONFIG_OPENTHREAD_LOG_LEVEL_DEBG", "y")


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
            cv.Required(CONF_NETWORK_KEY): cv.string_strict,
            cv.Required(CONF_PANID): cv.int_,
            cv.Required(CONF_XPANID): cv.int_,

        }
    ),
    set_core_data,
)
