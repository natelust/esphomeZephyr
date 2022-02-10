#pragma once

#define SSD1680_DRIVER_CONTROL 0x01
#define SSD1680_GATE_VOLTAGE 0x03
#define SSD1680_SOURCE_VOLTAGE 0x04
#define SSD1680_PROGOTP_INITIAL 0x08
#define SSD1680_PROGREG_INITIAL 0x09
#define SSD1680_READREG_INITIAL 0x0A
#define SSD1680_BOOST_SOFTSTART 0x0C
#define SSD1680_DEEP_SLEEP 0x10
#define SSD1680_DATA_MODE 0x11
#define SSD1680_SW_RESET 0x12
#define SSD1680_TEMP_CONTROL 0x18
#define SSD1680_TEMP_WRITE 0x1A
#define SSD1680_MASTER_ACTIVATE 0x20
#define SSD1680_DISP_CTRL1 0x21
#define SSD1680_DISP_CTRL2 0x22
#define SSD1680_WRITE_RAM1 0x24
#define SSD1680_WRITE_RAM2 0x26
#define SSD1680_WRITE_VCOM 0x2C
#define SSD1680_READ_OTP 0x2D
#define SSD1680_READ_STATUS 0x2F
#define SSD1680_WRITE_LUT 0x32
#define SSD1680_WRITE_BORDER 0x3C
#define SSD1680_SET_RAMXPOS 0x44
#define SSD1680_SET_RAMYPOS 0x45
#define SSD1680_SET_RAMXCOUNT 0x4E
#define SSD1680_SET_RAMYCOUNT 0x4F

namespace esphome {
namespace adafruit_epaper {

static const unsigned char ssd1680_default_init_code[] {
    SSD1680_SW_RESET, 0, // soft reset
    0xFF, 20,          // busy wait
    SSD1680_DATA_MODE, 1, 0x03, // Ram data entry mode
    SSD1680_WRITE_BORDER, 1, 0x05, // border color

    SSD1680_WRITE_VCOM, 1, 0x36,   // Vcom Voltage
    SSD1680_GATE_VOLTAGE, 1, 0x17, // Set gate voltage 
    SSD1680_SOURCE_VOLTAGE, 3, 0x41, 0x00, 0x32,   // Set source voltage

    SSD1680_SET_RAMXCOUNT, 1, 1,
    SSD1680_SET_RAMYCOUNT, 2, 0, 0,
    0xFE};

} // adafruit_epaper
} // esphome