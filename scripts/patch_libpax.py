"""ADV-only compatibility patch for pinned libpax 95758df72ad7981afdff76d1b7f06d4593c77345.

Retain the upstream license. Stop must release its FreeRTOS timer before losing
its handle; keyboard pause/settings otherwise allocate a new timer each time.
Expose the existing reset implementation through the public API as well.
"""
from pathlib import Path

TIMER_OLD = '  xTimerStop(PaxReportTimer, 0);\n  PaxReportTimer = NULL;'
TIMER_NEW = '''  // Cardputer compatibility: release the timer, not only its active state.
  if (xTimerDelete(PaxReportTimer, portMAX_DELAY) != pdPASS) {
    return -1; // retain the handle if the daemon queue rejects deletion
  }
  PaxReportTimer = NULL;'''
API_OLD = 'int libpax_counter_stop();'
API_NEW = '''int libpax_counter_stop();

// Existing libpax implementation, exposed for local counter controls.
void libpax_counter_reset();'''


BLE_OLD = """    /* A queue for storing received HCI packets. */
    ble_adv_dropped = 0;
    adv_queue = xQueueCreate(BLE_ADV_QUEUE_SIZE, sizeof(host_rcv_data_t));
    if (adv_queue == NULL) {
      ESP_LOGE(TAG, "Queue creation failed");
      return;
    }

    /* start HCI event processor task with prio 1 */
    xTaskCreate(&hci_evt_process, "hci_evt_process", 2048, NULL, 1,
                &hci_eventprocessor);

"""
BLE_NEW = """    /* Cardputer: keep exactly one queue and consumer across scan restarts.
     * The consumer owns static parse buffers, so duplicate consumers are unsafe.
     * Retain these resources while paused; never delete a running parser. */
    ble_adv_dropped = 0;
    if (adv_queue == NULL) {
      adv_queue = xQueueCreate(BLE_ADV_QUEUE_SIZE, sizeof(host_rcv_data_t));
    }
    if (adv_queue != NULL && hci_eventprocessor == NULL) {
      if (xTaskCreate(&hci_evt_process, "hci_evt_process", 2048, NULL, 1,
                      &hci_eventprocessor) != pdPASS) {
        vQueueDelete(adv_queue);
        adv_queue = NULL;
        hci_eventprocessor = NULL;
      }
    }
    if (adv_queue == NULL || hci_eventprocessor == NULL) {
      ESP_LOGE(TAG, "BLE queue/task allocation failed");
#ifdef LIBPAX_ARDUINO
      btStop();
#endif
#ifdef LIBPAX_ESPIDF
      esp_bt_controller_disable();
      esp_bt_controller_deinit();
#endif
      return;
    }

"""

def patch_text(text, old, new):
    """Accept exactly one known original or already patched region."""
    if text.count(new) == 1 and text.replace(new, '').count(old) == 0:
        return text
    if new in text or text.count(old) != 1:
        raise ValueError('Unexpected libpax source; inspect the pinned dependency before building')
    return text.replace(old, new, 1)


def patch_library(root):
    directory = Path(root) / 'lib' / 'libpax'
    changes = []
    for name, old, new in [('libpax_api.cpp', TIMER_OLD, TIMER_NEW),
                           ('libpax_api.h', API_OLD, API_NEW),
                           ('blescan.cpp', BLE_OLD, BLE_NEW)]:
        path = directory / name
        original = path.read_text()
        changes.append((path, original, patch_text(original, old, new)))
    # Validate all files before modifying any.
    for path, original, patched in changes:
        if patched != original:
            path.write_text(patched)


# PlatformIO injects Import when loading extra_scripts; unit tests do not.
if 'Import' in globals():
    Import('env')
    patch_library(Path(env.subst('$PROJECT_LIBDEPS_DIR')) / env.subst('$PIOENV') / 'libpax')
