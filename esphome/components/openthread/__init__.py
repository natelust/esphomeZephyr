from voluptuous.error import InInvalid
from voluptuous.schema_builder import Required
from esphome.components.zephyr import ZEPHYR_CORE_KEY
from esphome.const import (KEY_CORE, KEY_TARGET_PLATFORM)

from esphome.core import CORE, EsphomeError, coroutine_with_priority
import esphome.config_validation as cv
import esphome.codegen as cg


AUTO_LOAD = ["network", "openthread_srp"]

CONF_NETWORK_NAME = "network_name"
CONF_NETWORK_CHANNEL = "network_channel"
CONF_NETWORK_KEY = "network_key"
CONF_PANID = "panID"
CONF_XPANID = "xpanID"


def set_core_data(config):
    cv.only_on_zephyr(config)
    board = CORE.zephyr_manager.board
    if not board.can_openthread():
        raise cv.Invalid(f"Zephyr Board {board} cannot use OpenThread")
    manager = CORE.zephyr_manager
    manager.add_Kconfig_vec((
        ('CONFIG_NETWORKING', "y"),
        ('CONFIG_OPENTHREAD_CHANNEL', config[CONF_NETWORK_CHANNEL]),
        ('CONFIG_OPENTHREAD_NETWORK_NAME', f'"{config[CONF_NETWORK_NAME]}"'),
        ('CONFIG_OPENTHREAD_XPANID', f'"{config[CONF_XPANID]}"'),
        ('CONFIG_OPENTHREAD_PANID', config[CONF_PANID]),
        ("CONFIG_OPENTHREAD_NETWORKKEY", f'"{config[CONF_NETWORK_KEY]}"'),
        ('CONFIG_OPENTHREAD_JOINER', "y"),
        ("CONFIG_OPENTHREAD_THREAD_VERSION_1_2", "y"),
        ("CONFIG_OPENTHREAD_SRP_CLIENT", "y"),
        ("CONFIG_OPENTHREAD_SHELL", "n"),
        #("CONFIG_SHELL_STACK_SIZE", 3072),
        #("CONFIG_SHELL_ARGC_MAX", 26),
        #("CONFIG_SHELL_CMD_BUFF_SIZE", 416),
        ("CONFIG_NET_IPV4", "n"),
        ("CONFIG_NET_IPV6", "y"),
        ("CONFIG_NET_UDP", "y"),
        ("CONFIG_NET_TCP", "y"),
        ("CONFIG_OPENTHREAD_TCP_ENABLE", "y"),
        ("CONFIG_NET_SOCKETS", "y"),
        ("CONFIG_NET_CONFIG_SETTINGS", "y"),
        ("CONFIG_SETTINGS_RUNTIME", "y"),
        ("CONFIG_NET_SOCKETS_POSIX_NAMES", "y"),
        ("CONFIG_NET_SOCKETS_POLL_MAX", 4),
        #("CONFIG_NET_SHELL", "y"),
        ("CONFIG_NET_CONFIG_NEED_IPV6", "y"),
        ("CONFIG_NET_CONFIG_NEED_IPV4", "n"),
        ("CONFIG_NET_IF_UNICAST_IPV6_ADDR_COUNT", 20),
        ("CONFIG_NET_IF_MCAST_IPV6_ADDR_COUNT", 20),
        ("CONFIG_OPENTHREAD_IP6_MAX_EXT_UCAST_ADDRS", 10),
        ("CONFIG_OPENTHREAD_IP6_MAX_EXT_MCAST_ADDRS", 10),
        ("CONFIG_NVS", "y"),
        ("CONFIG_SETTINGS_NVS", "y"),
        ("CONFIG_ARM_MPU", "n"),
        #("CONFIG_NET_LOG", "y"),
        ("CONFIG_OPENTHREAD_THREAD_STACK_SIZE", 6144),
        ('CONFIG_MBEDTLS_HEAP_SIZE', 15240),
        ("CONFIG_OPENTHREAD_DHCP6_CLIENT", "y"),
        #("CONFIG_OPENTHREAD_DNS_CLIENT", "y"),
        #("CONFIG_DNS_RESOLVER", "y"),
        ("CONFIG_NET_CONNECTION_MANAGER", "y"),
        ("CONFIG_NET_PKT_RX_COUNT", 16),
        ("CONFIG_NET_PKT_TX_COUNT", 16),
        ("CONFIG_NET_BUF_RX_COUNT", 100),
        ("CONFIG_NET_BUF_TX_COUNT", 100),
        ("CONFIG_NET_CONTEXT_NET_PKT_POOL", "y"),
        ("CONFIG_OPENTHREAD_SLAAC", "y"),
        ("CONFIG_NET_IPV6_MLD", "n"),
        ("CONFIG_NET_IPV6_NBR_CACHE", "n"),
        #("CONFIG_MDNS_RESOLVER", "y"),
        #("CONFIG_LLMNR_RESOLVER", "y"),
        ("CONFIG_NET_L2_OPENTHREAD", "y"),
        ("CONFIG_OPENTHREAD_CLI_TCP_ENABLE", "n")

    ))

    """
    #add_Kconfig("CONFIG_OPENTHREAD_DEBUG", "y")
    add_Kconfig("CONFIG_OPENTHREAD_L2_DEBUG", "y")
    #add_Kconfig("CONFIG_OPENTHREAD_LOG_LEVEL_INFO", "y")
    add_Kconfig("CONFIG_OPENTHREAD_L2_LOG_LEVEL_INF", "y")
    add_Kconfig("CONFIG_NET_CORE_LOG_LEVEL_DBG", "y")
    add_Kconfig("CONFIG_OPENTHREAD_L2_LOG_LEVEL_DBG", "y")

    add_Kconfig("CONFIG_NET_IF_LOG_LEVEL_DBG", "y")
    add_Kconfig("CONFIG_NET_MGMT_EVENT_LOG_LEVEL_INF", "y")
    add_Kconfig("CONFIG_NET_IPV6_LOG_LEVEL_DBG", "y")
    add_Kconfig("CONFIG_NET_CONFIG_LOG_LEVEL_DBG", "y")
    """


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


@coroutine_with_priority(60.0)
async def to_code(cofnig):
    cg.add_define("LWIP_IPV6")
    cg.add_define("USE_OPENTHREAD")
    cg.add_global(cg.RawStatement("#include <net/openthread.h>"))
