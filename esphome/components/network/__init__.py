import esphome.codegen as cg
from esphome.core import CORE
from ..zephyr import add_Kconfig

CODEOWNERS = ["@esphome/core"]
AUTO_LOAD = ["mdns"]

network_ns = cg.esphome_ns.namespace("network")
IPAddress = network_ns.class_("IPAddress")

if CORE.is_zephyr:
    add_Kconfig("CONFIG_NETWORKING", "y")
    add_Kconfig("CONFIG_NET_UDP", "y")
    add_Kconfig("CONFIG_NET_TCP", "y")
    add_Kconfig("CONFIG_NET_HOSTNAME_ENABLE", "y")
    add_Kconfig("CONFIG_NET_HOSTNAME", f'"{CORE.name}"')
