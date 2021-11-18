import esphome.config_validation as cv
import esphome.codegen as cg
from esphome.core import CORE

CODEOWNERS = ["@esphome/core"]

CONF_IMPLEMENTATION = "implementation"
IMPLEMENTATION_LWIP_TCP = "lwip_tcp"
IMPLEMENTATION_BSD_SOCKETS = "bsd_sockets"

CONFIG_SCHEMA = cv.Schema(
    {
        cv.SplitDefault(
            CONF_IMPLEMENTATION,
            esp8266=IMPLEMENTATION_LWIP_TCP,
            esp32=IMPLEMENTATION_BSD_SOCKETS,
        ): cv.one_of(
            IMPLEMENTATION_LWIP_TCP, IMPLEMENTATION_BSD_SOCKETS, lower=True, space="_"
        ),
    }
)


def process_zephyr():
    from ..zephyr.const import ZEPHYR_CORE_KEY, KCONFIG_KEY

    Kconfigs = CORE.data[ZEPHYR_CORE_KEY][KCONFIG_KEY]
    Kconfigs["CONFIG_NET_SOCKETS"] = "y"


async def to_code(config):
    impl = config[CONF_IMPLEMENTATION]
    if impl == IMPLEMENTATION_LWIP_TCP:
        cg.add_define("USE_SOCKET_IMPL_LWIP_TCP")
    elif impl == IMPLEMENTATION_BSD_SOCKETS:
        cg.add_define("USE_SOCKET_IMPL_BSD_SOCKETS")
        if CORE.is_zephyr:
            process_zephyr()
