import esphome.codegen as cg

KEY_ESP32 = "esp32"
KEY_BOARD = "board"
KEY_VARIANT = "variant"
KEY_SDKCONFIG_OPTIONS = "sdkconfig_options"

VARIANT_ESP32 = "ESP32"
VARIANT_ESP32S2 = "ESP32S2"
VARIANT_ESP32S3 = "ESP32S3"
VARIANT_ESP32C3 = "ESP32C3"
VARIANT_ESP32H2 = "ESP32H2"
VARIANTS = [
    VARIANT_ESP32,
    VARIANT_ESP32S2,
    VARIANT_ESP32S3,
    VARIANT_ESP32C3,
    VARIANT_ESP32H2,
]

esp32_ns = cg.esphome_ns.namespace("esp32")
