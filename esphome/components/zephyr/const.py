import esphome.codegen as cg

ZEPHYR_CORE_KEY = 'zephyr'
ZEPHYR_FRAMEWORK_DEFUALT_VERSION = "2.6.0"
KEY_BOARD = "board"
ZEPHYR_BASE = "zephyr_base"
KCONFIG_KEY = "Kconfigs"

zephyr_ns = cg.global_ns.namespace("esphome").namespace("zephyr")
