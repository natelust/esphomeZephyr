#pragma once

#include "esphome/core/hal.h"
#include <drivers/gpio.h>
#include <vector>

namespace esphome {
namespace zephyr{

class CallBackWrapper {
  private:
    void (*func)(void *);
    void *arg;
  public:
   void operator () (const struct device *dev, struct gpio_callback *cb, uint32_t pins) {
     this->func(this->arg);
   }
};

class ZephyrGPIOPin : public InternalGPIOPin{
 public:
  void set_pin(uint8_t pin) { pin_ = pin; }
  void set_inverted(bool inverted) { inverted_ = inverted; }
  void set_flags(gpio::Flags flags) { flags_ = flags; }
  void set_device(struct device * device) {this->device = device;}
  void setup() override { pin_mode(flags_); }
  void pin_mode(gpio::Flags flags) override;
  bool digital_read() override;
  void digital_write(bool value) override;
  std::string dump_summary() const override;
  void detach_interrupt() const override;
  ISRInternalGPIOPin to_isr() const override;
  uint8_t get_pin() const override { return pin_; }
  bool is_inverted() const override { return inverted_; }

 protected:
  void attach_interrupt(void (*func)(void *), void *arg, gpio::InterruptType type) const override;

  uint8_t pin_;
  bool inverted_;
  gpio::Flags flags_;
  struct device * device = nullptr;
  CallBackWrapper * callback = nullptr;
  static struct gpio_callback pin_callback_struct;
  
};

}  // namespace zephyr
}  // namespace esphome