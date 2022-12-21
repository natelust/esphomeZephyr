#include "ot_srp.h"
#include "esphome/core/log.h"

#include <openthread/thread.h>
#include <openthread/srp_client_buffers.h>
#include <openthread/netdata.h>

namespace esphome {
namespace openthread {

void OpenThreadSRP::setup() {
    uint16_t len = host_name.size();
    otError error;
    int aborted = 1;
    uint16_t size;
    char *   existing_host_name;
    uint8_t       arrayLength;
    otIp6Address *hostAddressArray;
    std::string service = "_esphomelib._tcp";
    otSrpClientBuffersServiceEntry *entry = nullptr;
    char *                          string;
    char *                          label;
    const otIp6Address * localIp = nullptr;
    const otIp6Prefix * omrPrefix = nullptr;
    otBorderRouterConfig aConfig;
    otNetworkDataIterator iterator = OT_NETWORK_DATA_ITERATOR_INIT;
    const otNetifAddress *unicastAddrs = nullptr;

    uint8_t ip_found = 0;
    char addressAsString[40];
    uint16_t timeout_counter = 0;

    struct openthread_context * context = openthread_get_default_context();
    // lock the mutex
    openthread_api_mutex_lock(context);

    // set the host name
    existing_host_name = otSrpClientBuffersGetHostNameString(context->instance, &size);

    if (len > size) { 
        ESP_LOGW("OT_SRP", "Hostname is too long, choose a shorter project name");
        goto exit;
    }

    memcpy(existing_host_name, host_name.c_str(), len + 1);
    error = otSrpClientSetHostName(context->instance, existing_host_name);
    if (error != 0){
        ESP_LOGW("OT_SRP", "Could not set host name with srp server");
        goto exit;
    }

    // set the ip address
    // get the link local ip address
    //localIp = otThreadGetLinkLocalIp6Address(context->instance);
    //localIp = otThreadGetMeshLocalEid(context->instance);
    while (otNetDataGetNextOnMeshPrefix(context->instance, &iterator, &aConfig) != OT_ERROR_NONE) {
        openthread_api_mutex_unlock(context);
        k_msleep(100);
        openthread_api_mutex_lock(context);
        // After 5 seconds, if there are no addresses, continue boot
        if (timeout_counter > 50) {
            ESP_LOGW("OT_SRP", "Could not find the ip address of this device");
            goto exit;
        }
        timeout_counter++;
    };
    if (error != 0){
        ESP_LOGW("OT_SRP", "Could not get the OMR prefix");
        goto exit;
    }
    omrPrefix = &aConfig.mPrefix;
    otIp6PrefixToString(omrPrefix, addressAsString, 40);
    ESP_LOGW("OT_SRP", "USING omr prefix %s", addressAsString);
    unicastAddrs = otIp6GetUnicastAddresses(context->instance);
    for (const otNetifAddress *addr = unicastAddrs; addr; addr = addr->mNext){
        localIp = &addr->mAddress;
        if (otIp6PrefixMatch(&omrPrefix->mPrefix, localIp)) {
            ip_found = 1;
            otIp6AddressToString(localIp, addressAsString, 40);
            ESP_LOGW("OT_SRP", "USING %s for SRP address", addressAsString);
            break;
        }
    }
    if (ip_found == 0) {
        ESP_LOGW("OT_SRP", "Could not find the OMR address");
        goto exit;
    }

    hostAddressArray = otSrpClientBuffersGetHostAddressesArray(context->instance, &arrayLength);

    memcpy(hostAddressArray, localIp, sizeof(*localIp));
    error = otSrpClientSetHostAddresses(context->instance, hostAddressArray, arrayLength);
    if (error != 0){
        ESP_LOGW("OT_SRP", "Could not set ip address with srp server");
        goto exit;
    }

    // set the records
    entry = otSrpClientBuffersAllocateService(context->instance);
    entry->mService.mPort = 6053;

    string = otSrpClientBuffersGetServiceEntryInstanceNameString(entry, &size);
    memcpy(string, host_name.c_str(), strlen(host_name.c_str()));

    string = otSrpClientBuffersGetServiceEntryServiceNameString(entry, &size);
    memcpy(string, service.c_str(), strlen(service.c_str()));

    label = strchr(string, ',');
    entry->mService.mNumTxtEntries = 0;
    error = otSrpClientAddService(context->instance, &entry->mService);
    if (error != 0){
        ESP_LOGW("OT_SRP", "Could not set service to advertise.");
        goto exit;
    }

    otSrpClientEnableAutoStartMode(context->instance, nullptr, nullptr);
    // unlock the mutex
    aborted = 0;
exit:
    if (aborted) {
        this->mark_failed();
        ESP_LOGW("OT_SRP", "Setting SRP record failed, clear partial state");
        k_msleep(100);
        otSrpClientClearHostAndServices(context->instance);
        otSrpClientBuffersFreeAllServices(context->instance);
    }
    openthread_api_mutex_unlock(context);
}

void OpenThreadSRP::set_host_name(std::string host_name){
    this->host_name = host_name;
}

}  // namespace openthread
}  // namespace esphome