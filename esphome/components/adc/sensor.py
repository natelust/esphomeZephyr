import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import pins
from esphome.components import sensor, voltage_sampler
from esphome.const import (
    CONF_ATTENUATION,
    CONF_ID,
    CONF_INPUT,
    CONF_PIN,
    CONF_REF,
    CONF_RESOLUTION,
    CONF_VOLTAGE,
    DEVICE_CLASS_VOLTAGE,
    STATE_CLASS_MEASUREMENT,
    UNIT_VOLT,
    CONF_GAIN
)
from esphome.core import CORE


AUTO_LOAD = ["voltage_sampler"]

ATTENUATION_MODES = {
    "0db": cg.global_ns.ADC_ATTEN_DB_0,
    "2.5db": cg.global_ns.ADC_ATTEN_DB_2_5,
    "6db": cg.global_ns.ADC_ATTEN_DB_6,
    "11db": cg.global_ns.ADC_ATTEN_DB_11,
}

ZEPHYR_GAINS = {
    "1/6": "ADC_GAIN_1_6",
    "1/5": "ADC_GAIN_1_5",
    "1/4": "ADC_GAIN_1_4",
    "1/3": "ADC_GAIN_1_3",
    "1/2": "ADC_GAIN_1_2",
    "2/3": "ADC_GAIN_2_3",
    "1": "ADC_GAIN_1",
    "2": "ADC_GAIN_2",
    "3": "ADC_GAIN_3",
    "4": "ADC_GAIN_4",
    "6": "ADC_GAIN_6",
    "8": "ADC_GAIN_8",
    "12": "ADC_GAIN_12",
    "16": "ADC_GAIN_16",
    "24": "ADC_GAIN_24",
    "32": "ADC_GAIN_32",
    "64": "ADC_GAIN_64",
    "128": "ADC_GAIN_128",
}

ZEPHYR_REF = {
	"vdd_1": "ADC_REF_VDD_1",     # VDD
	"vdd_1/2": "ADC_REF_VDD_1_2",   # VDD/2.
	"vdd_1/3": "ADC_REF_VDD_1_3",   # VDD/3.
	"vdd_1/4": "ADC_REF_VDD_1_4",   # VDD/4.
	"internal": "ADC_REF_INTERNAL",  # Internal.
	"external0": "ADC_REF_EXTERNAL0", # External, input 0.
	"external1": "ADC_REF_EXTERNAL1", # External, input 1.
}


def validate_adc_pin(value):
    if str(value).upper() == "VCC":
        return cv.only_on_esp8266("VCC")

    if CORE.is_esp32:
        from esphome.components.esp32 import is_esp32c3

        value = pins.internal_gpio_input_pin_number(value)
        if is_esp32c3():
            if not (0 <= value <= 4):  # ADC1
                raise cv.Invalid("ESP32-C3: Only pins 0 though 4 support ADC.")
        elif not (32 <= value <= 39):  # ADC1
            raise cv.Invalid("ESP32: Only pins 32 though 39 support ADC.")
    elif CORE.is_esp8266:
        from esphome.components.esp8266.gpio import CONF_ANALOG

        value = pins.internal_gpio_pin_number({CONF_ANALOG: True, CONF_INPUT: True})(
            value
        )

        if value != 17:  # A0
            raise cv.Invalid("ESP8266: Only pin A0 (GPIO17) supports ADC.")
        return pins.gpio_pin_schema(
            {CONF_ANALOG: True, CONF_INPUT: True}, internal=True
        )(value)
    elif CORE.is_zephyr:
        manager = CORE.zephyr_manager
        manager.board.validate_adc_pin(value)
        value = pins.internal_gpio_input_pin_number(value)
        return value
    else:
        raise NotImplementedError

    return pins.internal_gpio_input_pin_schema(value)


adc_ns = cg.esphome_ns.namespace("adc")
ADCSensor = adc_ns.class_(
    "ADCSensor", sensor.Sensor, cg.PollingComponent, voltage_sampler.VoltageSampler
)

CONFIG_SCHEMA = (
    sensor.sensor_schema(
        unit_of_measurement=UNIT_VOLT,
        accuracy_decimals=2,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
    )
    .extend(
        {
            cv.GenerateID(): cv.declare_id(ADCSensor),
            cv.Required(CONF_PIN): validate_adc_pin,
            cv.SplitDefault(CONF_ATTENUATION, esp32="0db"): cv.All(
                cv.only_on_esp32, cv.enum(ATTENUATION_MODES, lower=True)
            ),
            cv.SplitDefault(CONF_GAIN, zephyr="1"): cv.All(
                str,
                cv.only_on_zephyr,
                cv.enum(ZEPHYR_GAINS)
            ),
            cv.SplitDefault(CONF_REF, zephyr="internal"): cv.All(
                str,
                cv.only_on_zephyr,
                cv.enum(ZEPHYR_REF)
            ),
            cv.SplitDefault(CONF_RESOLUTION, zephyr=10): cv.All(
                int,
                cv.only_on_zephyr,
                cv.one_of(8,10,12, 14)
            ),
            cv.SplitDefault(CONF_VOLTAGE, zephyr=3.3): cv.All(
                float,
                cv.only_on_zephyr,
            ),
        }
    )
    .extend(cv.polling_component_schema("60s"))
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await sensor.register_sensor(var, config)

    if CORE.is_zephyr:
        device_name, pin = CORE.zephyr_manager.handle_adc(**config)
        cg.add(var.set_pin(pin))
        cg.add(var.set_gain(cg.RawExpression(config[CONF_GAIN].enum_value)))
        cg.add(var.set_reference(cg.RawExpression(config[CONF_REF].enum_value)))
        cg.add(var.set_resolution(config[CONF_RESOLUTION]))
        cg.add(var.set_device(cg.RawExpression(f"DT_LABEL(DT_NODELABEL({device_name}))")))
        cg.add(var.set_ref_voltage(config[CONF_VOLTAGE]))
    else:
        if config[CONF_PIN] == "VCC":
            cg.add_define("USE_ADC_SENSOR_VCC")
        else:
            pin = await cg.gpio_pin_expression(config[CONF_PIN])
            cg.add(var.set_pin(pin))

        if CONF_ATTENUATION in config:
            cg.add(var.set_attenuation(config[CONF_ATTENUATION]))
