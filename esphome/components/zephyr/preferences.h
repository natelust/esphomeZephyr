#pragma once

#ifdef USE_ZEPHYR

namespace esphome {
namespace zephyr {
    void setup_preferences();
    void preferences_prevent_write(bool prevent);

}  // namespace zephyr
}  // namespace esphome

#endif  //USE_ZEPHYR