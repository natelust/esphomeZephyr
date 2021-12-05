import esphome.codegen as cg
from esphome.core import CORE

CODEOWNERS = ["@esphome/core"]
if not CORE.is_zephyr:
    # should really only disable this if openthread set, for now
    # do it everywehre to test
    AUTO_LOAD = ["mdns"]

network_ns = cg.esphome_ns.namespace("network")
IPAddress = network_ns.class_("IPAddress")

if CORE.is_zephyr:
    manager = CORE.zephyr_manager
    assert manager is not None
    manager.add_Kconfig_vec((
        ("CONFIG_NETWORKING", "y"),
        ("CONFIG_NET_UDP", "y"),
        ("CONFIG_NET_TCP", "y"),
        ("CONFIG_NET_HOSTNAME_ENABLE", "y"),
        ("CONFIG_NET_HOSTNAME", f'"{CORE.name}"'),
    ))
