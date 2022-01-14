#pragma once

#include "esphome/core/component.h"
#include "esphome/core/hal.h"
#include "esphome/core/defines.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/voltage_sampler/voltage_sampler.h"

//#ifdef USE_ZEPHYR
#include <drivers/adc.h>
//#endif

#ifdef USE_ESP32
#include "driver/adc.h"
#endif

namespace esphome {
namespace adc {

class ADCSensor : public sensor::Sensor, public PollingComponent, public voltage_sampler::VoltageSampler {
 public:
#ifdef USE_ESP32
  /// Set the attenuation for this pin. Only available on the ESP32.
  void set_attenuation(adc_atten_t attenuation);
#endif

  /// Update adc values.
  void update() override;
  /// Setup ADc
  void setup() override;
  void dump_config() override;
  /// `HARDWARE_LATE` setup priority.
  float get_setup_priority() const override;
  #ifndef USE_ZEPHYR
  void set_pin(InternalGPIOPin *pin) { this->pin_ = pin; }
  #else
  void set_pin(int pin) {this->pin_= pin;}
  void set_gain(adc_gain gain) {this->gain_ = gain;}
  void set_reference(adc_reference ref) {this->ref_ = ref;}
  void set_resolution(uint8_t resolution) {this->resolution_ = resolution;}
  void set_device(std::string device) { this->dev_ = device_get_binding(device.c_str()) ;}
  void set_ref_voltage(float ref_volts);
  #endif
  float sample() override;

#ifdef USE_ESP8266
  std::string unique_id() override;
#endif

 protected:
#ifndef USE_ZEPHYR
  InternalGPIOPin *pin_;
#else
  uint8_t pin_;
  adc_gain gain_;
  adc_reference ref_;
  const struct device * dev_ = nullptr;
  struct adc_channel_cfg config_;
  uint8_t resolution_ = 10;
  uint16_t  ref_mvolt_;
#endif

#ifdef USE_ESP32
  adc_atten_t attenuation_{ADC_ATTEN_DB_0};
#endif
};

}  // namespace adc
}  // namespace esphome
