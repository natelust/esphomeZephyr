#pragma once

#include "adafruit_epaper.h"

#ifdef USE_THINKINK_213_TRICOLOR_RW
#include "ssd1680.h"

#define THINKINK_213_TRICOLOR_RW_WIDTH 250
#define THINKINK_213_TRICOLOR_RW_HEIGHT 122


namespace esphome {
namespace adafruit_epaper {

static const char * const THINKINK_213_TAG = "display.thinkink213";

class ThinkInk_213_Tricolor_RW :
        public AdafruitEPaper<THINKINK_213_TRICOLOR_RW_WIDTH,
                              THINKINK_213_TRICOLOR_RW_HEIGHT, true> {

    void setup() override {
        init_code = ssd1680_default_init_code;
        AdafruitEPaper<THINKINK_213_TRICOLOR_RW_WIDTH,
                       THINKINK_213_TRICOLOR_RW_HEIGHT, true>::setup();

        ESP_LOGD(THINKINK_213_TAG, "setting up the display");
    }

    void power_up() override {
        ESP_LOGD(THINKINK_213_TAG, "Powering up display");
        uint8_t buf[5];

        hardware_reset();
        delay(100);
        busy_wait();

        const uint8_t *init_co = this->init_code;

        if (_epd_init_code != NULL) {
            init_co = _epd_init_code;
        }
        init_commands();

        // Set ram X start/end postion
        buf[0] = 0x01;
        buf[1] = (THINKINK_213_TRICOLOR_RW_HEIGHT + 6) / 8;
        command(SSD1680_SET_RAMXPOS, buf, 2);

        // Set ram Y start/end postion
        buf[0] = 0x00;
        buf[1] = 0x00;
        buf[2] = (THINKINK_213_TRICOLOR_RW_WIDTH - 1);
        buf[3] = (THINKINK_213_TRICOLOR_RW_WIDTH - 1) >> 8;
        command(SSD1680_SET_RAMYPOS, buf, 4);

        // Set display size and driver output control
        buf[0] = (THINKINK_213_TRICOLOR_RW_WIDTH - 1);
        buf[1] = (THINKINK_213_TRICOLOR_RW_WIDTH - 1) >> 8;
        buf[2] = 0x00;
        command(SSD1680_DRIVER_CONTROL, buf, 3);
        ESP_LOGD(THINKINK_213_TAG, "Display powered");
    }

    void power_down() override {
        ESP_LOGD(THINKINK_213_TAG, "Powering down display");
        uint8_t buf[1];
        // Only deep sleep if we can get out of it
        if (reset_pin_ != nullptr) {
            ESP_LOGD(THINKINK_213_TAG, "deep sleeping");
            // deep sleep
            buf[0] = 0x01;
            command(SSD1680_DEEP_SLEEP, buf, 1);
            delay(100);
        } else {
            ESP_LOGD(THINKINK_213_TAG, "sw reset");
            command(SSD1680_SW_RESET);
            busy_wait();
        }
        ESP_LOGD(THINKINK_213_TAG, "Powered down");
    }

    void update_display() override {
        ESP_LOGD(THINKINK_213_TAG, "Updating display");
        uint8_t buf[1];

        // display update sequence
        buf[0] = 0xF4;
        command(SSD1680_DISP_CTRL2, buf, 1);

        command(SSD1680_MASTER_ACTIVATE);
        busy_wait();
        if (this->busy_pin_ == nullptr) {
            delay(1000);
        }
    }

    void start_write(Buffer buf_number) override {
        ESP_LOGD(THINKINK_213_TAG, "Beginning write");
        if (buf_number == Buffer::BLACK) {
            command(SSD1680_WRITE_RAM1, true);
        }
        if (buf_number == Buffer::COLOR) {
            command(SSD1680_WRITE_RAM2, true);
        }
    }

    void set_ram_address(uint16_t x, uint16_t y) {
        ESP_LOGD(THINKINK_213_TAG, "Setting Ram Address");
        (void)x;
        (void)y;

        uint8_t buf[2];

        // set RAM x address count
        buf[0] = 1;
        command(SSD1680_SET_RAMXCOUNT, buf, 1);

        // set RAM y address count
        buf[0] = 0;
        buf[1] = 0;
        command(SSD1680_SET_RAMYCOUNT, buf, 2);
    }

    bool is_color(Color color) override {
        if (color.r > 0) {
            return true;
        } else {
            return false;
        }
    }

    bool is_black(Color color) override {
        return (color.r <= 120) && (color.g == 0) && (color.b == 0);
    }
};

} // namespace adafruit_epaper
} // namespace esphome
#endif