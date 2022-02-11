#include "spi.h"
#ifdef USE_ZEPHYR
#include "esphome/core/helpers.h"
#include "esphome/core/application.h"
#include <string>

namespace esphome {
namespace spi {

static const char *const TAG = "spi_zephyr";

void SPIComponent::disable() {
    int result = spi_release(device, config);
    if (result != 0) {
        ESP_LOGD(TAG, "Dirver seems to have already unlocked device");
    }
    delete this->config;
    this->config = nullptr;
    if (this->active_cs_ != nullptr) {
        this->active_cs_->digital_write(true);
        this->active_cs_ = nullptr;
    }
}

template<SPIBitOrder BIT_ORDER, SPIClockPolarity CLOCK_POLARITY, SPIClockPhase CLOCK_PHASE, uint32_t DATA_RATE>
void SPIComponent::enable(GPIOPin *cs) {
    if (this->config != nullptr) {
        ESP_LOGE(TAG, "Previous transaction not closed, aborting enable");
        return;
    }
    this->config = new spi_config {
        .frequency = DATA_RATE,
        .operation = SPI_OP_MODE_MASTER | SPI_WORD_SET(8) | SPI_LOCK_ON
    };

    if (BIT_ORDER == SPIBitOrder::BIT_ORDER_LSB_FIRST) {
        this->config->operation |= SPI_TRANSFER_LSB;
    } else {
        this->config->operation |= SPI_TRANSFER_MSB;
    }

    if (CLOCK_POLARITY == SPIClockPolarity::CLOCK_POLARITY_HIGH ) {
        this->config->operation |= SPI_MODE_CPOL;
    }
    if ( CLOCK_PHASE == SPIClockPhase::CLOCK_PHASE_TRAILING) {
        this->config->operation |= SPI_MODE_CPHA;
    }


    if (cs != nullptr) {
        this->active_cs_ = cs;
        this->active_cs_->digital_write(false);
    }
}

/*
void SPIComponent::setup() {
    ESP_LOGCONFIG(TAG, "Setting up SPI bus...");    
    int i = 0;
    i++;

}

void SPIComponent::dump_config() {
    ESP_LOGCONFIG(TAG, "SPI bus:");
    
}

float SPIComponent::get_setup_priority() const { return setup_priority::BUS; }
*/

template<ZephyrDirectionControl dir>
void SPIComponent::transceive_(uint8_t * data, size_t length) {
    if (config == nullptr) {
        ESP_LOGE(TAG, "Enable not called prior to transaction, aborting");
        return;
    }
    const struct spi_buf local_buf = {
        .buf = data,
        .len = length,
    };

    const struct spi_buf_set buffer = {
        .buffers = &local_buf,
        .count = 1,
    };

    std::string name;
    int result;
    switch(dir) {
        case ZephyrDirectionControl::READ:
            result = spi_read(device, config, &buffer);
            name = "read";
            break;
        case ZephyrDirectionControl::WRITE:
            result = spi_write(device, config, &buffer);
            name = "write";
            break;
        case ZephyrDirectionControl::BOTH:
            uint8_t * read_arr = new uint8_t [length];

            const struct spi_buf local_read_buf = {
                .buf = read_arr,
                .len = length
            };

            const struct spi_buf_set read_buff = {
                .buffers = &local_read_buf,
                .count = 1
            };
            name = "transfer";
            result = spi_transceive(device, config, &buffer, &read_buff);
            if (result == 0) {
                memcpy(data, read_arr, length);
            }
            delete read_arr;
    }
    if (result != 0) {
        ESP_LOGCONFIG(TAG, "SPI %s failed", name.c_str());
    }
}

// Generate with (py3):
//
// from itertools import product
// bit_orders = ['BIT_ORDER_LSB_FIRST', 'BIT_ORDER_MSB_FIRST']
// clock_pols = ['CLOCK_POLARITY_LOW', 'CLOCK_POLARITY_HIGH']
// clock_phases = ['CLOCK_PHASE_LEADING', 'CLOCK_PHASE_TRAILING']
// reads = [False, True]
// writes = [False, True]
// cpp_bool = {False: 'false', True: 'true'}
// for b, cpol, cph, r, w in product(bit_orders, clock_pols, clock_phases, reads, writes):
//     if not r and not w:
//         continue
//     print(f"template uint8_t ZephyrSPIComponent::transfer_<{b}, {cpol}, {cph}, {cpp_bool[r]}, {cpp_bool[w]}>(uint8_t
//     data);")


/*
from itertools import product

bit_orders = ["BIT_ORDER_LSB_FIRST", "BIT_ORDER_MSB_FIRST"]

clock_pols = ["CLOCK_POLARITY_LOW", "CLOCK_POLARITY_HIGH"]

clock_phases = ["CLOCK_PHASE_LEADING", "CLOCK_PHASE_TRAILING"]

data_rate = ['1000', '75000', '200000', '1000000', '2000000', '4000000', '8000000', '10000000', '20000000', '40000000']


for b, cpol, cph, dr in product(bit_orders, clock_pols, clock_phases, da
ta_rate):
    print(
        f"template void SPIComponent::enable<{b}, {cpol}, {cph}, {dr} >(GPIOPin *cs);"
    )

*/

template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_LEADING, 1000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_LEADING, 75000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_LEADING, 200000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_LEADING, 1000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_LEADING, 2000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_LEADING, 4000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_LEADING, 8000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_LEADING, 10000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_LEADING, 20000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_LEADING, 40000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_TRAILING, 1000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_TRAILING, 75000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_TRAILING, 200000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_TRAILING, 1000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_TRAILING, 2000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_TRAILING, 4000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_TRAILING, 8000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_TRAILING, 10000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_TRAILING, 20000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_TRAILING, 40000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_LEADING, 1000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_LEADING, 75000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_LEADING, 200000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_LEADING, 1000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_LEADING, 2000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_LEADING, 4000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_LEADING, 8000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_LEADING, 10000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_LEADING, 20000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_LEADING, 40000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_TRAILING, 1000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_TRAILING, 75000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_TRAILING, 200000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_TRAILING, 1000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_TRAILING, 2000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_TRAILING, 4000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_TRAILING, 8000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_TRAILING, 10000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_TRAILING, 20000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_LSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_TRAILING, 40000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_LEADING, 1000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_LEADING, 75000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_LEADING, 200000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_LEADING, 1000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_LEADING, 2000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_LEADING, 4000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_LEADING, 8000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_LEADING, 10000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_LEADING, 20000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_LEADING, 40000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_TRAILING, 1000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_TRAILING, 75000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_TRAILING, 200000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_TRAILING, 1000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_TRAILING, 2000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_TRAILING, 4000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_TRAILING, 8000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_TRAILING, 10000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_TRAILING, 20000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_LOW, CLOCK_PHASE_TRAILING, 40000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_LEADING, 1000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_LEADING, 75000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_LEADING, 200000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_LEADING, 1000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_LEADING, 2000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_LEADING, 4000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_LEADING, 8000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_LEADING, 10000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_LEADING, 20000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_LEADING, 40000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_TRAILING, 1000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_TRAILING, 75000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_TRAILING, 200000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_TRAILING, 1000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_TRAILING, 2000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_TRAILING, 4000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_TRAILING, 8000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_TRAILING, 10000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_TRAILING, 20000000 >(GPIOPin *cs);
template void SPIComponent::enable<BIT_ORDER_MSB_FIRST, CLOCK_POLARITY_HIGH, CLOCK_PHASE_TRAILING, 40000000 >(GPIOPin *cs);

template void SPIComponent::transceive_<ZephyrDirectionControl::READ>(uint8_t * data, size_t length);
template void SPIComponent::transceive_<ZephyrDirectionControl::WRITE>(uint8_t * data, size_t length);
template void SPIComponent::transceive_<ZephyrDirectionControl::BOTH>(uint8_t * data, size_t length);


} // namespace spi
} // namespace esphome

#endif