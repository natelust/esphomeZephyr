#pragma once
#include "spi_const.h"
#include "esphome/core/defines.h"

/*
#ifdef USE_ZEPHYR
#include "spi_zephyr.h"
#else
#include "spi_esp.h"
#endif
*/
#include "spi_base.h"

namespace esphome {
namespace spi {

template<SPIBitOrder BIT_ORDER, SPIClockPolarity CLOCK_POLARITY, SPIClockPhase CLOCK_PHASE, SPIDataRate DATA_RATE>
class SPIDevice {
 public:
  SPIDevice() = default;

/*
#ifdef USE_ZEPHYR
  SPIDevice(ZephyrSPIComponent *parent, GPIOPin *cs) : parent_(parent), cs_(cs) {}
  void set_spi_parent(ZephyrSPIComponent *parent) { parent_ = parent; }
#else
  SPIDevice(ESPSPIComponent *parent, GPIOPin *cs) : parent_(parent), cs_(cs) {}
  void set_spi_parent(ESPSPIComponent *parent) { parent_ = parent; }
#endif
*/
  SPIDevice(SPIComponent *parent, GPIOPin *cs) : parent_(parent), cs_(cs) {}
  void set_spi_parent(SPIComponent *parent) { parent_ = parent; }
  void set_cs_pin(GPIOPin *cs) { cs_ = cs; }

  void spi_setup() {
    if (this->cs_) {
      this->cs_->setup();
      this->cs_->digital_write(true);
    }
  }

  void enable() { this->parent_->template enable<BIT_ORDER, CLOCK_POLARITY, CLOCK_PHASE, DATA_RATE>(this->cs_); }

  void disable() { this->parent_->disable(); }

  uint8_t read_byte() { return this->parent_->template read_byte<BIT_ORDER, CLOCK_POLARITY, CLOCK_PHASE>(); }

  void read_array(uint8_t *data, size_t length) {
    return this->parent_->template read_array<BIT_ORDER, CLOCK_POLARITY, CLOCK_PHASE>(data, length);
  }

  template<size_t N> std::array<uint8_t, N> read_array() {
    std::array<uint8_t, N> data;
    this->read_array(data.data(), N);
    return data;
  }

  void write_byte(uint8_t data) {
    return this->parent_->template write_byte<BIT_ORDER, CLOCK_POLARITY, CLOCK_PHASE>(data);
  }

  void write_byte16(uint16_t data) {
    return this->parent_->template write_byte16<BIT_ORDER, CLOCK_POLARITY, CLOCK_PHASE>(data);
  }

  void write_array16(const uint16_t *data, size_t length) {
    this->parent_->template write_array16<BIT_ORDER, CLOCK_POLARITY, CLOCK_PHASE>(data, length);
  }

  void write_array(const uint8_t *data, size_t length) {
    this->parent_->template write_array<BIT_ORDER, CLOCK_POLARITY, CLOCK_PHASE>(data, length);
  }

  template<size_t N> void write_array(const std::array<uint8_t, N> &data) { this->write_array(data.data(), N); }

  void write_array(const std::vector<uint8_t> &data) { this->write_array(data.data(), data.size()); }

  uint8_t transfer_byte(uint8_t data) {
    return this->parent_->template transfer_byte<BIT_ORDER, CLOCK_POLARITY, CLOCK_PHASE>(data);
  }

  void transfer_array(uint8_t *data, size_t length) {
    this->parent_->template transfer_array<BIT_ORDER, CLOCK_POLARITY, CLOCK_PHASE>(data, length);
  }

  template<size_t N> void transfer_array(std::array<uint8_t, N> &data) { this->transfer_array(data.data(), N); }

 protected:
 SPIComponent *parent_{nullptr};
/*
#ifdef USE_ZEPHYR
  ZephyrSPIComponent *parent_{nullptr};
#else
  ESPSPIComponent *parent_{nullptr};
#endif*/
  GPIOPin *cs_{nullptr};
};

} // namespace spi
} // namespace esphome