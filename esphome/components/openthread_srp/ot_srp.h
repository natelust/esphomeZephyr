#pragma once

#include "esphome/core/component.h"

#include <net/openthread.h>
#include <openthread/srp_client.h>

namespace esphome {
namespace openthread_srp {

class OpenThreadSRP : public Component {
    public:
        void setup() override;
        float get_setup_priority() const override {
            return setup_priority::HARDWARE
        }
    protected:
};

}  // namespace openthread_srp
}  // namespace esphome