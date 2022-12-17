//#ifdef USE_ZEPHYR

#include "i2c_bus_zephyr.h"
#include "esphome/core/log.h"

namespace esphome{
namespace i2c {

static const char *const TAG = "i2c.zephyr";

void ZephyrI2CBus::setup() {
    if (device == nullptr) {
        ESP_LOGE(TAG, "I2C device not initialized");
        mark_failed();
    } else {
        i2c_configure(device, I2C_MODE_MASTER|I2C_SPEED_SET(I2C_SPEED_STANDARD));
        recover_();
        initialized_ = true;
    }
}

void ZephyrI2CBus::dump_config() {
    ESP_LOGCONFIG(TAG, "I2C Bus:");
    ESP_LOGCONFIG(TAG, "  SDA Pin: GPIO%s", this->sda_pin_.c_str());
    ESP_LOGCONFIG(TAG, "  SCL Pin: GPIO%s", this->scl_pin_.c_str());
    ESP_LOGCONFIG(TAG, "  Frequency: %u Hz", this->frequency_);
    switch (this->recovery_result_) {
        case ZephyrRecoveryCode::ZRC_SUCCESS:
            ESP_LOGCONFIG(TAG, "  Recovery: bus successfully recovered");
            break;
        case ZephyrRecoveryCode::ZRC_EBUSY:
            ESP_LOGCONFIG(TAG, "  Recover: failed, bus is not yet cleared, busy");
            break;
        case ZephyrRecoveryCode::ZRC_EIO:
            ESP_LOGCONFIG(TAG, "  Recovery: failed, error in i/o");
            break;
        case ZephyrRecoveryCode::ZRC_ENOSYS:
            ESP_LOGCONFIG(TAG, "  Recovery: failed, recovery not implemented on this board");
            break;
    }
    if (this->scan_) {
        ESP_LOGI(TAG, "Scanning i2c bus for active devices...");
        uint8_t found = 0;
        for (uint8_t address = 8; address < 120; address++) {
            struct i2c_msg msgs[1];
            uint8_t dst;

            msgs[0].buf = &dst;
            msgs[0].len = 0U;
            msgs[0].flags = I2C_MSG_WRITE | I2C_MSG_STOP;
            if (i2c_transfer(device, &msgs[0], 1, address) == 0) {
                ESP_LOGI(TAG, "Found i2c device at address 0x%02X", address);
                found++;
            }

        }
        if (found == 0) {
            ESP_LOGI(TAG, "Found no i2c devices!");
        }
        ESP_LOGI(TAG, "Above errors are normal and a side effect of probing addresses");
    }
}

void ZephyrI2CBus::recover_() {
  ESP_LOGI(TAG, "Performing I2C bus recovery");
  int result = i2c_recover_bus(this->device);
  this->recovery_result_ = static_cast<ZephyrRecoveryCode>(result);

}

ErrorCode ZephyrI2CBus::read(uint8_t address, uint8_t *buffer, size_t len) {
    int result = i2c_read(this->device, buffer, len, address);
    if (result == 0) {
        return ErrorCode::ERROR_OK;
    }else {
        return ErrorCode::ERROR_UNKNOWN;
    }
}

ErrorCode ZephyrI2CBus::readv(uint8_t address, ReadBuffer *buffers, size_t cnt) {
    /*
    i2c_msg * msgs = new i2c_msg[cnt];
    for (size_t i=0; i < cnt; ++i) {
        msgs[i].buf = const_cast<uint8_t *>(buffers[i].data);
        msgs[i].len = buffers[i].len;
        msgs[i].flags = I2C_MSG_READ;
    }
    msgs[cnt-1].flags |= I2C_MSG_STOP;
    int result = i2c_transfer(device, msgs, cnt, address);
    ESP_LOGE(TAG, "Read error %d", result);
    delete msgs;
    if (result == 0) {
        return ErrorCode::ERROR_OK;
    }else {
        return ErrorCode::ERROR_UNKNOWN;
    }
    */
    return transfer_<ReadBuffer *, I2C_MSG_READ>(address, buffers, cnt);
}

ErrorCode ZephyrI2CBus::write(uint8_t address, const uint8_t *buffer, size_t len) {
    int result = i2c_write(this->device, buffer, len, address);
    if (result == 0) {
        return ErrorCode::ERROR_OK;
    }else {
        return ErrorCode::ERROR_UNKNOWN;
    }
}


ErrorCode ZephyrI2CBus::writev(uint8_t address, WriteBuffer *buffers, size_t cnt) {
    /*
    i2c_msg * msgs = new i2c_msg[cnt];
    for (size_t i=0; i < cnt; ++i) {
        msgs[i].buf = const_cast<uint8_t *>(buffers[i].data);
        msgs[i].len = buffers[i].len;
        msgs[i].flags = I2C_MSG_WRITE;
    }
    msgs[cnt-1].flags |= I2C_MSG_STOP;
    int result = i2c_transfer(device, msgs, cnt, address);
    delete msgs;
    if (result == 0) {
        return ErrorCode::ERROR_OK;
    }else {
        return ErrorCode::ERROR_UNKNOWN;
    }
    */
    return transfer_<WriteBuffer *, I2C_MSG_WRITE>(address, buffers, cnt);
}

ErrorCode ZephyrI2CBus::writev(uint8_t address, WriteBuffer *buffers, size_t cnt, bool stop) {
    return transfer_<WriteBuffer *, I2C_MSG_WRITE>(address, buffers, cnt);
}

template<typename T, unsigned int I>
ErrorCode ZephyrI2CBus::transfer_(uint8_t address, T buffers, size_t cnt) {
    i2c_msg * msgs = new i2c_msg[cnt];
    for (size_t i=0; i < cnt; ++i) {
        msgs[i].buf = const_cast<uint8_t *>(buffers[i].data);
        msgs[i].len = buffers[i].len;
        msgs[i].flags = I;
    }
    msgs[cnt-1].flags |= I2C_MSG_STOP;
    int result = i2c_transfer(device, msgs, cnt, address);
    delete msgs;
    if (result == 0) {
        return ErrorCode::ERROR_OK;
    }else {
        return ErrorCode::ERROR_UNKNOWN;
    }
}


} // namespace i2c
} // namespace esphome

//#endif