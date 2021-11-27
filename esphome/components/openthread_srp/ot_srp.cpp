#include "ot_srp.h"

namespace esphome {
namespace openthread_srp {

OpenThreadSRP::setup() {
    struct openthread_context * context = openthread_get_default_context();
    // lock the mutex
    openthread_api_mutex_lock(context);
    // unlock the mutex
    openthread_api_mutex_unlock(context);
}

}  // namespace openthread_srp
}  // namespace esphome