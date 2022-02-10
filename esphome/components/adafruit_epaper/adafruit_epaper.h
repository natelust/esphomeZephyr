#pragma once

#include "esphome/core/defines.h"
#include "esphome/core/component.h"
#include "esphome/components/spi/spi.h"
#include "esphome/components/display/display_buffer.h"

namespace esphome {
namespace adafruit_epaper {

enum Buffer {
    BLACK = 0,
    COLOR = 1
};

template <int WIDTH, int HEIGHT, bool COLOR>
class AdafruitEPaper : public Component,
                       public display::DisplayBuffer,
                       public spi::SPIDevice<spi::BIT_ORDER_MSB_FIRST,
                                           spi::CLOCK_POLARITY_LOW,
                                           spi::CLOCK_PHASE_LEADING,
                                           spi::DATA_RATE_4MHZ> {
  public:
    void set_dc_pin(GPIOPin *dc_pin) { this->dc_pin_ = dc_pin; }
    void set_reset_pin(GPIOPin *reset) { this->reset_pin_ = reset; }
    void set_busy_pin(GPIOPin *busy) { this->busy_pin_ = busy; }

    float get_setup_priority() const override;

    void display();
    void clear();

    void on_safe_shutdown() override;
    void setup() override;

    void busy_wait();

  protected:
    //void draw_absolute_pixel_internal(int x, int y, Color color) override;
    void write_framebuffer_to_display(Buffer buf_number, bool invert=false);
    void command(uint8_t cmd, bool end=true);
    void command(uint8_t cmd, const uint8_t *buf, uint16_t length);
    void clear_buffers();
    void init_commands();
    void hardware_reset();
    void draw_absolute_pixel_internal(int x, int y, Color color) override;

    int get_height_internal() override {
        return _HEIGHT;
    }

    int get_width_internal() override {
        return WIDTH;
    }

    // Methods to be overridden by subclasses
    virtual void power_up() = 0;
    virtual void power_down() = 0;
    virtual void update_display();
    virtual void start_write(Buffer buf_number) = 0;
    virtual void setRAMAddress(uint16_t x, uint16_t y) = 0;
    //virtual uint8_t * get_buffer_from_number(Buffer buf_num) = 0;

    // class members
    GPIOPin *reset_pin_ = nullptr;
    GPIOPin *dc_pin_ = nullptr;
    GPIOPin *busy_pin_ = nullptr;

    const static uint16_t _HEIGHT = HEIGHT + (HEIGHT % 8 != 0) * (8 - (HEIGHT % 8));

    const static uint32_t buffer_size = WIDTH*_HEIGHT/8;
    uint8_t black_buffer[buffer_size];
    const uint8_t * init_code = nullptr;
    bool invert_black_color[2] = {true, false};
    uint8_t * _epd_init_code = nullptr;
    // use only a single byte if color is not needed
    uint8_t color_buffer[COLOR*buffer_size];
};
} // namespace adafruit_epaper
} // namespace esphome