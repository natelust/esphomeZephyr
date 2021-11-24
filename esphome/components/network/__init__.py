import esphome.codegen as cg
from esphome.core import CORE
from ..zephyr import add_Kconfig

CODEOWNERS = ["@esphome/core"]
if not CORE.is_zephyr:
    # should really only disable this if openthread set, for now
    # do it everywehre to test
    AUTO_LOAD = ["mdns"]

network_ns = cg.esphome_ns.namespace("network")
IPAddress = network_ns.class_("IPAddress")

if CORE.is_zephyr:
    add_Kconfig("CONFIG_NETWORKING", "y")
    add_Kconfig("CONFIG_NET_UDP", "y")
    add_Kconfig("CONFIG_NET_TCP", "y")
    add_Kconfig("CONFIG_NET_HOSTNAME_ENABLE", "y")
    add_Kconfig("CONFIG_NET_HOSTNAME", f'"{CORE.name}"')
