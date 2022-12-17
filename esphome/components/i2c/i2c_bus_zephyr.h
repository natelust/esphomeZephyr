#pragma once
#include "i2c_bus.h"
#include "esphome/core/component.h"
#include <zephyr/drivers/i2c.h>
#include <string>
#include <zephyr/devicetree.h>

namespace esphome {
namespace i2c {

enum ZephyrRecoveryCode {
    ZRC_SUCCESS,
    ZRC_EBUSY,
    ZRC_EIO,
    ZRC_ENOSYS
};

class ZephyrI2CBus : public I2CBus, public Component {
  public:
    void setup() override;
    void dump_config() override;
    float get_setup_priority() const override { return setup_priority::BUS; }
    void set_scan(bool scan) { scan_ = scan; }

    ErrorCode read(uint8_t address, uint8_t *buffer, size_t len);
    ErrorCode readv(uint8_t address, ReadBuffer *buffers, size_t cnt);

    ErrorCode write(uint8_t address, const uint8_t *buffer, size_t len);
    ErrorCode writev(uint8_t address, WriteBuffer *buffers, size_t cnt);
    ErrorCode writev(uint8_t address, WriteBuffer *buffers, size_t cnt, bool stop);

    void set_device(std::string device) {this->device = device_get_binding(device.c_str());}
    void set_sda_pin(std::string sda_pin) { sda_pin_ = sda_pin; }
    void set_scl_pin(std::string scl_pin) { scl_pin_ = scl_pin; }
    void set_frequency(uint32_t frequency) { frequency_= frequency; }
  private:
    void recover_();
  protected:
    const struct device * device = nullptr;
    bool scan_;
    bool initialized_ = false;
    std::string sda_pin_;
    std::string scl_pin_;
    uint32_t frequency_;
    ZephyrRecoveryCode recovery_result_;
    template<typename T, unsigned int I>
    ErrorCode transfer_(uint8_t address, T buffers, size_t cnt);
};

} // namespace i2c
} // namepace esphome