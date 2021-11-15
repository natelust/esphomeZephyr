#include "gpio.h"
#include <sys/util.h>

namespace esphome {
namespace zephyr {

struct ISRPinArg {
  uint8_t pin;
  bool inverted;
};

void pin_callback(const struct device *port, struct gpio_callback *cb, gpio_port_pins_t pins){
  struct GPIOInterruptWrapper * container = CONTAINER_OF(cb, struct GPIOInterruptWrapper, pin_callback_struct);
  container->func(container->arg);

}

ISRInternalGPIOPin ZephyrGPIOPin::to_isr() const {
  auto *arg = new ISRPinArg{};  // NOLINT(cppcoreguidelines-owning-memory)
  arg->pin = pin_;
  arg->inverted = inverted_;
  return ISRInternalGPIOPin((void *) arg);
}

void ZephyrGPIOPin::attach_interrupt(void (*func)(void *), void *arg, esphome::gpio::InterruptType type) const {
    uint32_t gpio_controller_mode = 0;
    switch (type) {
        case esphome::gpio::INTERRUPT_RISING_EDGE:
            gpio_controller_mode = inverted_ ? GPIO_INT_EDGE_FALLING : GPIO_INT_EDGE_RISING;
            break;
        case esphome::gpio::INTERRUPT_FALLING_EDGE:
            gpio_controller_mode = inverted_ ? GPIO_INT_EDGE_RISING : GPIO_INT_EDGE_FALLING;
            break;
        case esphome::gpio::INTERRUPT_ANY_EDGE:
            gpio_controller_mode = GPIO_INT_EDGE_BOTH;
            break;
        case esphome::gpio::INTERRUPT_LOW_LEVEL:
            gpio_controller_mode = inverted_ ? GPIO_INT_LEVEL_HIGH: GPIO_INT_LEVEL_LOW;
            break;
        case esphome::gpio::INTERRUPT_HIGH_LEVEL:
            gpio_controller_mode = inverted_ ? GPIO_INT_LEVEL_LOW : GPIO_INT_LEVEL_HIGH;
            break;
    }
    gpio_pin_interrupt_configure(this->device, pin_, gpio_controller_mode); // todo

    this->wrapper->func = func;
    this->wrapper->arg = arg;
    gpio_init_callback(&(this->wrapper->pin_callback_struct), pin_callback, BIT(pin_));
    gpio_add_callback(this->device, &(this->wrapper->pin_callback_struct));
}

void ZephyrGPIOPin::pin_mode(gpio::Flags flags) {
  uint32_t mode;
  if (flags == gpio::FLAG_INPUT) {
    mode = GPIO_INPUT;
  } else if (flags == gpio::FLAG_OUTPUT) {
    mode = GPIO_OUTPUT;
  } else if (flags == (gpio::FLAG_INPUT | gpio::FLAG_PULLUP)) {
    mode = GPIO_INPUT | GPIO_PULL_UP;
  } else if (flags == (gpio::FLAG_INPUT | gpio::FLAG_PULLDOWN)) {
    mode = GPIO_INPUT | GPIO_PULL_DOWN;
  } else if (flags == (gpio::FLAG_OUTPUT | gpio::FLAG_OPEN_DRAIN)) {
    mode = GPIO_OUTPUT | GPIO_OPEN_DRAIN;
  } else {
    return;
  }
  gpio_pin_configure(this->device, pin_, mode);
}

std::string ZephyrGPIOPin::dump_summary() const {
  char buffer[32];
  snprintf(buffer, sizeof(buffer), "GPIO%u", pin_);
  return buffer;
}

bool ZephyrGPIOPin::digital_read() {
  return bool(gpio_pin_get_raw(this->device, this->pin_)) != inverted_; 
}
void ZephyrGPIOPin::digital_write(bool value) {
  gpio_pin_set_raw(this->device, pin_, value != inverted_ ? 1 : 0);  // NOLINT
}
void ZephyrGPIOPin::detach_interrupt() const {
  gpio_remove_callback(this->device, &(this->wrapper->pin_callback_struct));
}

}  // namespace zephyr
}  // namespace esphome