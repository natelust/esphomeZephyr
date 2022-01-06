#pragma once
#ifndef USE_ZEPHYR

#include <vector>
#include "spi.h"

#ifdef USE_ARDUINO
#define USE_SPI_ARDUINO_BACKEND
#endif

#ifdef USE_SPI_ARDUINO_BACKEND
#include <SPI.h>
#endif

namespace esphome {
namespace spi {

class ESPSPIComponent : public SPIComponent, public Component {
 public:
  void set_clk(GPIOPin *clk) { clk_ = clk; }
  void set_miso(GPIOPin *miso) { miso_ = miso; }
  void set_mosi(GPIOPin *mosi) { mosi_ = mosi; }

  void setup() override;

  void dump_config() override;

  template<SPIBitOrder BIT_ORDER, SPIClockPolarity CLOCK_POLARITY, SPIClockPhase CLOCK_PHASE> uint8_t read_byte() {
#ifdef USE_SPI_ARDUINO_BACKEND
    if (this->hw_spi_ != nullptr) {
      return this->hw_spi_->transfer(0x00);
    }
#endif  // USE_SPI_ARDUINO_BACKEND
    return this->transfer_<BIT_ORDER, CLOCK_POLARITY, CLOCK_PHASE, true, false>(0x00);
  }

  template<SPIBitOrder BIT_ORDER, SPIClockPolarity CLOCK_POLARITY, SPIClockPhase CLOCK_PHASE>
  void read_array(uint8_t *data, size_t length) {
#ifdef USE_SPI_ARDUINO_BACKEND
    if (this->hw_spi_ != nullptr) {
      this->hw_spi_->transfer(data, length);
      return;
    }
#endif  // USE_SPI_ARDUINO_BACKEND
    for (size_t i = 0; i < length; i++) {
      data[i] = this->read_byte<BIT_ORDER, CLOCK_POLARITY, CLOCK_PHASE>();
    }
  }

  template<SPIBitOrder BIT_ORDER, SPIClockPolarity CLOCK_POLARITY, SPIClockPhase CLOCK_PHASE>
  void write_byte(uint8_t data) {
#ifdef USE_SPI_ARDUINO_BACKEND
    if (this->hw_spi_ != nullptr) {
      this->hw_spi_->write(data);
      return;
    }
#endif  // USE_SPI_ARDUINO_BACKEND
    this->transfer_<BIT_ORDER, CLOCK_POLARITY, CLOCK_PHASE, false, true>(data);
  }

  template<SPIBitOrder BIT_ORDER, SPIClockPolarity CLOCK_POLARITY, SPIClockPhase CLOCK_PHASE>
  void write_byte16(const uint16_t data) {
#ifdef USE_SPI_ARDUINO_BACKEND
    if (this->hw_spi_ != nullptr) {
      this->hw_spi_->write16(data);
      return;
    }
#endif  // USE_SPI_ARDUINO_BACKEND

    this->write_byte<BIT_ORDER, CLOCK_POLARITY, CLOCK_PHASE>(data >> 8);
    this->write_byte<BIT_ORDER, CLOCK_POLARITY, CLOCK_PHASE>(data);
  }

  template<SPIBitOrder BIT_ORDER, SPIClockPolarity CLOCK_POLARITY, SPIClockPhase CLOCK_PHASE>
  void write_array16(const uint16_t *data, size_t length) {
#ifdef USE_SPI_ARDUINO_BACKEND
    if (this->hw_spi_ != nullptr) {
      for (size_t i = 0; i < length; i++) {
        this->hw_spi_->write16(data[i]);
      }
      return;
    }
#endif  // USE_SPI_ARDUINO_BACKEND
    for (size_t i = 0; i < length; i++) {
      this->write_byte16<BIT_ORDER, CLOCK_POLARITY, CLOCK_PHASE>(data[i]);
    }
  }

  template<SPIBitOrder BIT_ORDER, SPIClockPolarity CLOCK_POLARITY, SPIClockPhase CLOCK_PHASE>
  void write_array(const uint8_t *data, size_t length) {
#ifdef USE_SPI_ARDUINO_BACKEND
    if (this->hw_spi_ != nullptr) {
      auto *data_c = const_cast<uint8_t *>(data);
      this->hw_spi_->writeBytes(data_c, length);
      return;
    }
#endif  // USE_SPI_ARDUINO_BACKEND
    for (size_t i = 0; i < length; i++) {
      this->write_byte<BIT_ORDER, CLOCK_POLARITY, CLOCK_PHASE>(data[i]);
    }
  }

  template<SPIBitOrder BIT_ORDER, SPIClockPolarity CLOCK_POLARITY, SPIClockPhase CLOCK_PHASE>
  uint8_t transfer_byte(uint8_t data) {
#ifdef USE_SPI_ARDUINO_BACKEND
    if (this->miso_ != nullptr) {
      if (this->hw_spi_ != nullptr) {
        return this->hw_spi_->transfer(data);
      } else {
        return this->transfer_<BIT_ORDER, CLOCK_POLARITY, CLOCK_PHASE, true, true>(data);
      }
    }
#endif  // USE_SPI_ARDUINO_BACKEND
    this->write_byte<BIT_ORDER, CLOCK_POLARITY, CLOCK_PHASE>(data);
    return 0;
  }

  template<SPIBitOrder BIT_ORDER, SPIClockPolarity CLOCK_POLARITY, SPIClockPhase CLOCK_PHASE>
  void transfer_array(uint8_t *data, size_t length) {
#ifdef USE_SPI_ARDUINO_BACKEND
    if (this->hw_spi_ != nullptr) {
      if (this->miso_ != nullptr) {
        this->hw_spi_->transfer(data, length);
      } else {
        this->hw_spi_->writeBytes(data, length);
      }
      return;
    }
#endif  // USE_SPI_ARDUINO_BACKEND

    if (this->miso_ != nullptr) {
      for (size_t i = 0; i < length; i++) {
        data[i] = this->transfer_byte<BIT_ORDER, CLOCK_POLARITY, CLOCK_PHASE>(data[i]);
      }
    } else {
      this->write_array<BIT_ORDER, CLOCK_POLARITY, CLOCK_PHASE>(data, length);
    }
  }

  template<SPIBitOrder BIT_ORDER, SPIClockPolarity CLOCK_POLARITY, SPIClockPhase CLOCK_PHASE, uint32_t DATA_RATE>
  void enable(GPIOPin *cs) {
#ifdef USE_SPI_ARDUINO_BACKEND
    if (this->hw_spi_ != nullptr) {
      uint8_t data_mode = (uint8_t(CLOCK_POLARITY) << 1) | uint8_t(CLOCK_PHASE);
      SPISettings settings(DATA_RATE, BIT_ORDER, data_mode);
      this->hw_spi_->beginTransaction(settings);
    } else {
#endif  // USE_SPI_ARDUINO_BACKEND
      this->clk_->digital_write(CLOCK_POLARITY);
      uint32_t cpu_freq_hz = arch_get_cpu_freq_hz();
      this->wait_cycle_ = uint32_t(cpu_freq_hz) / DATA_RATE / 2ULL;
#ifdef USE_SPI_ARDUINO_BACKEND
    }
#endif  // USE_SPI_ARDUINO_BACKEND

    if (cs != nullptr) {
      this->active_cs_ = cs;
      this->active_cs_->digital_write(false);
    }
  }

  void disable();

  float get_setup_priority() const override;

 protected:
  inline void cycle_clock_(bool value);

  template<SPIBitOrder BIT_ORDER, SPIClockPolarity CLOCK_POLARITY, SPIClockPhase CLOCK_PHASE, bool READ, bool WRITE>
  uint8_t transfer_(uint8_t data);

  GPIOPin *clk_;
  GPIOPin *miso_{nullptr};
  GPIOPin *mosi_{nullptr};
  GPIOPin *active_cs_{nullptr};
#ifdef USE_SPI_ARDUINO_BACKEND
  SPIClass *hw_spi_{nullptr};
#endif  // USE_SPI_ARDUINO_BACKEND
  uint32_t wait_cycle_;
};

}  // namespace spi
}  // namespace esphome

#endif