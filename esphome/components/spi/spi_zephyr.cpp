#ifdef USE_ZEPHYR
#include "esphome/core/log.h"
#include "esphome/core/helpers.h"
#include "esphome/core/application.h"
#include "spi_zephyr.h"
#include <string>

namespace esphome {
namespace spi {

static const char *const TAG = "spi_zephyr";

void ZephyrSPIComponent::disable() {
    int result = spi_release(device, &config);
    if (result != 0) {
        ESP_LOGE(TAG, "There was a problem releasing the SPI lock");
    }
    delete this->config;
    this->config = nullptr;
    if (this->active_cs_ != nullptr) {
        this->active_cs_->digital_write(true);
        this->active_cs_ = nullptr;
    }
}

template<SPIBitOrder BIT_ORDER, SPIClockPolarity CLOCK_POLARITY, SPIClockPhase CLOCK_PHASE, uint32_t DATA_RATE>
void ZephyrSPIComponent::enable(GPIOPin *cs) override {
    if (this->config != nullptr) {
        ESP_LOGE(TAG, "Previous transaction not closed, aborting enable");
        return;
    }
    this->config = new spi_config {
        .frequency=DATA_RATE,
        .operation = SPI_OP_MODE_MASTER | SPI_WORD_SET(8) | SPI_LOCK_ON
    };

    if (BIT_ORDER == SPIBitOrder::BIT_ORDER_LSB_FIRST) {
        this->config->operation |= SPI_TRANSFER_LSB;
    } else {
        this->config->operation |= SPI_TRANSFER_MSB;
    }

    if (CLOCK_POLARITY  == SPIClockPolarity::CLOCK_POLARITY_HIGH) {
        this->config->operation |= SPI_MODE_CPOL;
        if (CLOCK_PHASE == SPIClockPhase::CLOCK_PHASE_LEADING) {
            this->config->operation |= SPI_MODE_CPHA;
        }
    } else {
        if (CLOCK_PHASE == SPIClockPhase::CLOCK_PHASE_TRAILING) {
            this->config->operation |= SPI_MODE_CPHA;
        }
    }

    if (cs != nullptr) {
        this->active_cs_ = cs;
        this->active_cs_->digital_write(false);
    }
}

/*
void ZephyrSPIComponent::setup() {
    ESP_LOGCONFIG(TAG, "Setting up SPI bus...");    
    int i = 0;
    i++;

}

void ZephyrSPIComponent::dump_config() {
    ESP_LOGCONFIG(TAG, "SPI bus:");
    
}

float ZephyrSPIComponent::get_setup_priority() const { return setup_priority::BUS; }
*/

template<Direction dir>
void ZephyrSPIComponent::transceive_(uint8_t *data, size_t length) {
    if (config == nullptr) {
        ESP_LOGE(TAG, "Enable not called prior to transaction, aborting");
        return;
    }
    const struct spi_buf_set buffer = {
        .buffers = &(const struct spi_buf) {
            .buf = data
            .len = length,
        },
        .count = 1,
    };
    std::string name;
    int result;
    switch(dir) {
        case ZephyrDirectionControl::READ:
            result = spi_read(device, config, &buffer);
            name = "read";
            break;
        case ZephyrDirectionControl::Write:
            result = spi_write(device, config, &buffer)
            name = "write";
            break;
        case ZephyrDirectionControl::BOTH:
            uint8_t * read_arr = new unit8_t [length];
            const struct spi_buf_set read_buff = {
                .buffers = &(const struct spi_buf) {
                    .buf = read_arr
                    .len = length,
                },
                .count = 1
            };
            name = "transfer";
            result = spi_transceive(device, config, &buffer, read_buff);
            if (result != 0) {
                memcpy(data, read_arr, length);
            }
            delete read_arr;
    }
    if (result != 0) {
        ESP_LOGCONFIG(TAG, "SPI %s failed", name);
    }
}


} // namespace spi
} // namespace esphome

#endif