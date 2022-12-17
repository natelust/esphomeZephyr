//#ifdef USE_ZEPHYR

#include "esphome/core/hal.h"
#include "esphome/core/helpers.h"
#include "preferences.h"

#include <zephyr/kernel.h>
#include <zephyr/sys/reboot.h>

namespace esphome {
void yield() { k_yield(); }
uint32_t millis() { return k_uptime_get_32(); }
void delay(uint32_t ms) { k_sleep(K_MSEC(ms)); }
uint32_t micros() { return k_uptime_get_32() * 1000; }
void delayMicroseconds(uint32_t us) { k_sleep(K_USEC(us)); }
void arch_restart() {
    sys_reboot(SYS_REBOOT_COLD);
}
void arch_feed_wdt() {}
uint8_t progmem_read_byte(const uint8_t *addr) { return *addr; }

uint32_t arch_get_cpu_cycle_count() {
    return k_uptime_ticks();
}

uint32_t arch_get_cpu_freq_hz() { return sys_clock_hw_cycles_per_sec(); }

void force_link_symbols() {}

void resetPins() {}

void arch_init() {}
}
//#endif