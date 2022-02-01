#pragma once

#include "esphome/core/hal.h"


namespace esphome {
namespace spi {

/// The bit-order for SPI devices. This defines how the data read from and written to the device is interpreted.
enum SPIBitOrder {
  /// The least significant bit is transmitted/received first.
  BIT_ORDER_LSB_FIRST,
  /// The most significant bit is transmitted/received first.
  BIT_ORDER_MSB_FIRST,
};
/** The SPI clock signal polarity,
 *
 * This defines how the clock signal is used. Flipping this effectively inverts the clock signal.
 */
enum SPIClockPolarity {
  /** The clock signal idles on LOW. (CPOL=0)
   *
   * A rising edge means a leading edge for the clock.
   */
  CLOCK_POLARITY_LOW = false,
  /** The clock signal idles on HIGH. (CPOL=1)
   *
   * A falling edge means a trailing edge for the clock.
   */
  CLOCK_POLARITY_HIGH = true,
};
/** The SPI clock signal phase.
 *
 * This defines when the data signals are sampled. Most SPI devices use the LEADING clock phase.
 */
enum SPIClockPhase {
  /// The data is sampled on a leading clock edge. (CPHA=0)
  CLOCK_PHASE_LEADING,
  /// The data is sampled on a trailing clock edge. (CPHA=1)
  CLOCK_PHASE_TRAILING,
};
/** The SPI clock signal data rate. This defines for what duration the clock signal is HIGH/LOW.
 * So effectively the rate of bytes can be calculated using
 *
 * effective_byte_rate = spi_data_rate / 16
 *
 * Implementations can use the pre-defined constants here, or use an integer in the template definition
 * to manually use a specific data rate.
 */
enum SPIDataRate : uint32_t {
  DATA_RATE_1KHZ = 1000,
  DATA_RATE_75KHZ = 75000,
  DATA_RATE_200KHZ = 200000,
  DATA_RATE_1MHZ = 1000000,
  DATA_RATE_2MHZ = 2000000,
  DATA_RATE_4MHZ = 4000000,
  DATA_RATE_8MHZ = 8000000,
  DATA_RATE_10MHZ = 10000000,
  DATA_RATE_20MHZ = 20000000,
  DATA_RATE_40MHZ = 40000000,
};

} // namespace spi
} // namespace esphome