#pragma once

#include "esphome/core/hal.h"
#include "esphome/core/log.h"
#include <drivers/gpio.h>
#include <devicetree.h>
#include <vector>

namespace esphome {
namespace zephyr{

struct GPIOInterruptWrapper {
  gpio_callback pin_callback_struct;
  void (*func)(void *);
  void *arg;
};

class ZephyrGPIOPin : public InternalGPIOPin{
 public:
  void set_pin(uint8_t pin) { pin_ = pin; }
  void set_inverted(bool inverted) { inverted_ = inverted; }
  void set_flags(gpio::Flags flags) {
    flags_ = flags;
    // Set this here, as zephyr is fine with it, and
    // setup does not seem to be triggering for GPIO
    // devices
    this->pin_mode(this->flags_);
  }
  void set_device(const struct device * device) {this->device = device;}
  void set_device_label(const char * label) {
    this->set_device(device_get_binding(label));
  }
  void setup() override { this->pin_mode(this->flags_); }
  void pin_mode(gpio::Flags flags) override;
  bool digital_read() override;
  void digital_write(bool value) override;
  std::string dump_summary() const override;
  void detach_interrupt() const override;
  ISRInternalGPIOPin to_isr() const override;
  uint8_t get_pin() const override { return pin_; }
  bool is_inverted() const override { return inverted_; }

  ZephyrGPIOPin() {
    wrapper = new GPIOInterruptWrapper();
  }

  ~ZephyrGPIOPin() {
    delete wrapper;
  }

 protected:
  void attach_interrupt(void (*func)(void *), void *arg, gpio::InterruptType type) const override;

  private:
    uint8_t pin_;
    bool inverted_;
    gpio::Flags flags_;
    const struct device * device = nullptr;
    GPIOInterruptWrapper * wrapper;
  
};

}  // namespace zephyr
}  // namespace esphome