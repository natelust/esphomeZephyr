#pragma once
#ifdef USE_ZEPHYR

#include <drivers/spi.h>
#include <string>
#include "spi.h"


namespace esphome {
namespace spi {

enum ZephyrDirectionControl {READ, WRITE, BOTH};

class ZephyrSPIComponent : public SPIComponent, public Component {
  public:
  /*
    void setup() override;
    void dump_config() override;
    */
    void setup() override{
        ESP_LOGCONFIG("SPI", "Setting up SPI bus...");    
        int i = 0;
        i++;

    }

    void dump_config() override{
        ESP_LOGCONFIG("SPI", "SPI bus:");
        
    }

    // specific methods to zephyr implementation
    void set_device(std::string dev) {
        device = device_get_binding(dev.c_str());
    }

    void set_miso_name(std::string miso) {miso_str = miso;}
    void set_mosi_name(std::string mosi) {mosi_str = mosi;}
    void set_clk_name(std::string clk) {clk_str = clk;}

    // Implemented to fulfill interface but not used with zephyr
    void set_miso(GPIOPin *miso) {};
    void set_mosi(GPIOPin *mosi) {};
    void set_clk(GPIOPin *clk) {}

    //templates not needed with zephyr
    template<class... Types>
    uint8_t read_byte() {
        uint8_t rx[1];
        transceive_<ZephyrDirectionControl::READ>(rx, 1);
        return rx[1];
    }

    //templates not needed with zephyr
    template<class... Types>
    void read_array(uint8_t *data, size_t length) {
        transceive_<ZephyrDirectionControl::READ>(data, length);
    }

    //templates not needed with zephyr
    template<class... Types>
    void write_byte(uint8_t data) {
        uint8_t tx[1] = {data};
        transceive_<ZephyrDirectionControl::WRITE>(tx, 1);
    }

    //templates not needed with zephyr
    template<class... Types>
    void write_array(const uint8_t *data, size_t length) {
        transceive_<ZephyrDirectionControl::WRITE, const uint8_t *>(data, length);
    }

    //templates not needed with zephyr
    template<class... Types>
    void write_byte16(const uint16_t data) {
        this->write_byte(data >> 8);
        this->write_byte(data);
    }

    //templates not needed with zephyr
    template<class... Types>
    void write_array16(const uint16_t *data, size_t length) {
        for (size_t i = 0; i < length; i++) {
            this->write_byte16(data[i]);
        }
    }

    //templates not needed with zephyr
    template<class... Types>
    void transfer_array(uint8_t *data, size_t length) {
        transceive_<ZephyrDirectionControl::BOTH>(data, length);
    }

    //templates not needed with zephyr
    template<class... Types>
    uint8_t transfer_byte(uint8_t data) {
        uint8_t tx[1] = data;
        transceive_<ZephyrDirectionControl::BOTH>(&tx, 1);
        return tx[1];
    }

    template<SPIBitOrder BIT_ORDER, SPIClockPolarity CLOCK_POLARITY, SPIClockPhase CLOCK_PHASE, uint32_t DATA_RATE>
    void enable(GPIOPin *cs);

    void disable();

    //float get_setup_priority() const override;
    float get_setup_priority() const override { return setup_priority::BUS; }

  private:
    const struct device * device = nullptr;
    struct spi_config  * config = nullptr;
    GPIOPin * active_cs_ = nullptr;
    std::string mosi_str = "";
    std::string miso_str = "";
    std::string clk_str = "";

    template<ZephyrDirectionControl dir, typename data_type=uint8_t *>
    void transceive_(data_type data, size_t length);

};

} // namespace spi
} // namespace esphome
#endif