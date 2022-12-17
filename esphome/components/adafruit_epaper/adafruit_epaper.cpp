#include "adafruit_epaper.h"


namespace esphome {
namespace adafruit_epaper {

static const char * const TAG = "display.adafruit";

template <int WIDTH, int HEIGHT, bool COLOR>
void AdafruitEPaper<WIDTH, HEIGHT, COLOR>::busy_wait() {
    if (this->busy_pin_ != nullptr) {
        ESP_LOGD(TAG, "Hardware busy waiting");
        while (this->busy_pin_->digital_read()) {
            delay(10);
        }
    } else {
        delay(500);
    }
}

template <int WIDTH, int HEIGHT, bool COLOR>
float AdafruitEPaper<WIDTH, HEIGHT, COLOR>::get_setup_priority() const {
    return setup_priority::PROCESSOR;
}

template <int WIDTH, int HEIGHT, bool COLOR>
void AdafruitEPaper<WIDTH, HEIGHT, COLOR>::setup() {
    ESP_LOGD(TAG, "Initializing EPaper display");

    this->clear_buffers();
    this->cs_->digital_write(true);
    this->hardware_reset();

    this->power_down();
}

template <int WIDTH, int HEIGHT, bool COLOR>
void AdafruitEPaper<WIDTH, HEIGHT, COLOR>::write_framebuffer_to_display(Buffer buf_number, bool invert) {
    this->start_write(buf_number);
    this->dc_pin_->digital_write(true);

    uint8_t * buffer = buf_number == 0 ? black_buffer : color_buffer;

    for (uint32_t i = 0; i < buffer_size; ++i) {
        uint8_t data = buffer[i];
        if (invert) {
            data = ~data;
        }
        this->enable();
        this->write_byte(data);
        this->disable();
    }
}

template <int WIDTH, int HEIGHT, bool COLOR>
void AdafruitEPaper<WIDTH, HEIGHT, COLOR>::display() {
    this->power_up();
    this->set_ram_address(0, 0);
    this->write_framebuffer_to_display(Buffer::BLACK, false);
    if (COLOR) {
        this->set_ram_address(0, 0);
        this->write_framebuffer_to_display(Buffer::COLOR, false);
    }
    this->update_display();
    this->power_down();
}

template <int WIDTH, int HEIGHT, bool COLOR>
void AdafruitEPaper<WIDTH, HEIGHT, COLOR>::clear_buffers() {
    uint8_t black_value = this->invert_black_color[Buffer::BLACK] ? 0xFF : 0x00;
    memset(black_buffer, black_value, buffer_size);

    if (COLOR) {
        uint8_t color_value = this->invert_black_color[Buffer::COLOR] ? 0xFF : 0x00;
        memset(color_buffer, color_value, buffer_size);

    }
}

template <int WIDTH, int HEIGHT, bool COLOR>
void AdafruitEPaper<WIDTH, HEIGHT, COLOR>::clear() {
    ESP_LOGD(TAG, "clearing display");
    clear_buffers();
    //display();
    //delay(100);
    // do it again to remove ghosts
    //display();
}

template <int WIDTH, int HEIGHT, bool COLOR>
void AdafruitEPaper<WIDTH, HEIGHT, COLOR>::on_safe_shutdown() {
    this->clear();
}

template <int WIDTH, int HEIGHT, bool COLOR>
void AdafruitEPaper<WIDTH, HEIGHT, COLOR>::init_commands() {
    if (init_code == nullptr) {
        ESP_LOGE(TAG, "No init commands failed, component cant be initialized");
        this->mark_failed();
        return;
    }
    uint8_t buf[64];

    while (init_code[0] != 0xFE) {
        uint8_t cmd = init_code[0];
        init_code++;
        uint8_t num_args = init_code[0];
        init_code++;
        if (cmd == 0xFF) {
            busy_wait();
            delay(num_args);
            continue;
        }

        for (int i = 0; i < num_args; ++i) {
            buf[i] = init_code[0];
            init_code++;
        }
        command(cmd, buf, num_args);
    }
}


template <int WIDTH, int HEIGHT, bool COLOR>
void AdafruitEPaper<WIDTH, HEIGHT, COLOR>::command(uint8_t cmd, bool end) {
    this->cs_->digital_write(true);
    this->dc_pin_->digital_write(false);
    
    this->enable();
    this->write_byte(cmd);

    if (end) {
        this->disable();
    }
}

template <int WIDTH, int HEIGHT, bool COLOR>
void AdafruitEPaper<WIDTH, HEIGHT, COLOR>::command(uint8_t cmd, const uint8_t *buf, uint16_t length) {
    this->command(cmd, true);
    
    this->dc_pin_->digital_write(true);

    for (uint16_t i = 0; i < length; i++) {
        this->enable();
        this->write_byte(buf[i]);
        this->disable();
    }
    //this->disable();
    
}

template <int WIDTH, int HEIGHT, bool COLOR>
void AdafruitEPaper<WIDTH, HEIGHT, COLOR>::hardware_reset() {
    if (this->reset_pin_ != nullptr) {
        ESP_LOGD(TAG, "hardware reset");
        this->reset_pin_->digital_write(true);
        delay(10);
        this->reset_pin_->digital_write(false);
        delay(10);
        this->reset_pin_->digital_write(true);
    } else {
        ESP_LOGD(TAG, "no hardware reset available");

    }
}

template <int WIDTH, int HEIGHT, bool COLOR>
void AdafruitEPaper<WIDTH, HEIGHT, COLOR>::draw_absolute_pixel_internal(int x, int y, Color color){
    if ( x >= WIDTH || y >= HEIGHT) {
        return;
    }
    if ( x < 0 || y < 0 ) {
        return;
    }
    
    uint16_t offset = ((uint32_t)(WIDTH - 1 - x) * (uint32_t)_HEIGHT + y) / 8;

    uint8_t * black_buf_off = this->black_buffer + offset;
    uint8_t * color_buf_off = this->color_buffer + offset;

    if (this->is_black(color)) {
        if (this->invert_black_color[Buffer::BLACK]) {
            *black_buf_off &= ~(1 << (7 - y % 8));
        } else {
            *black_buf_off |= (1 << (7 - y % 8));
        }
    }
    
    if (COLOR) {
        if (this->is_color(color)) {
            if (!this->invert_black_color[Buffer::COLOR]) {
                *color_buf_off |= (1 << (7 - y % 8));
            } else {
                *color_buf_off &= ~(1 << (7 - y % 8));
            }
        }
    }
}

template <int WIDTH, int HEIGHT, bool COLOR>
void AdafruitEPaper<WIDTH, HEIGHT, COLOR>::update() {
    this->clear();
    if (this->page_ != nullptr) {
        this->page_->get_writer()(*this);
    } else if (this->writer_.has_value()) {
        (*this->writer_)(*this);
    }
    this->display();
}


#ifdef USE_THINKINK_213_TRICOLOR_RW
template void AdafruitEPaper<250, 122, true>::busy_wait();
template void AdafruitEPaper<250, 122, true>::setup();
template float AdafruitEPaper<250, 122, true>::get_setup_priority() const;
template void AdafruitEPaper<250, 122, true>::write_framebuffer_to_display(Buffer buf_number, bool invert);
template void AdafruitEPaper<250, 122, true>::display();
template void AdafruitEPaper<250, 122, true>::clear_buffers();
template void AdafruitEPaper<250, 122, true>::clear();
template void AdafruitEPaper<250, 122, true>::on_safe_shutdown();
template void AdafruitEPaper<250, 122, true>::init_commands();
template void AdafruitEPaper<250, 122, true>::command(uint8_t cmd, bool end);
template void AdafruitEPaper<250, 122, true>::command(uint8_t cmd, const uint8_t *buf, uint16_t length);
template void AdafruitEPaper<250, 122, true>::hardware_reset();
template void AdafruitEPaper<250, 122, true>::draw_absolute_pixel_internal(int x, int y, Color color);
template void AdafruitEPaper<250, 122, true>::update();
#endif

} // namespace adafruit_epaper
} // namespace esphome