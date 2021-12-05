from esphome.core import CORE, coroutine_with_priority
import esphome.config_validation as cv
import esphome.codegen as cg


def check_zephyr(value):
    value = cv.only_on_zephyr(value)
    manager = CORE.zephyr_manager
    manager.add_Kconfig_vec((
        ("CONFIG_MCUMGR", "y"),
        ("CONFIG_MCUMGR_CMD_IMG_MGMT", "y"),
        ("CONFIG_MCUMGR_CMD_OS_MGMT", "y"),
        ("CONFIG_SYSTEM_WORKQUEUE_STACK_SIZE", 2304),
        ("CONFIG_MCUMGR_SMP_UDP_IPV6", "y"),
        ("CONFIG_MCUMGR_SMP_UDP", "y"),
        ("CONFIG_MCUMGR_SMP_UDP_IPV6", "y"),
        #("CONFIG_MCUMGR_SMP_UDP_IPV4", "y"),
    ))
    return value


CONFIG_SCHEMA = cv.All(cv.Schema({}, check_zephyr))


@coroutine_with_priority(50.0)
async def to_code(config):
    manager = CORE.zephyr_manager
    assert manager is not None
    cg.add_define("USE_ZEPHYR_OTA")
