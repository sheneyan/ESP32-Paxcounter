import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('patch_libpax', Path(__file__).parents[1] / 'scripts/patch_libpax.py')
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class PatchTests(unittest.TestCase):
    def test_timer_delete_keeps_handle_on_queue_failure(self):
        source = 'prefix\n' + module.TIMER_OLD + '\nsuffix'
        result = module.patch_text(source, module.TIMER_OLD, module.TIMER_NEW)
        self.assertNotIn('xTimerStop(', result)
        self.assertLess(result.index('return -1;'), result.index('PaxReportTimer = NULL'))
        self.assertIn('xTimerDelete(PaxReportTimer, portMAX_DELAY)', result)
        self.assertEqual(result, module.patch_text(result, module.TIMER_OLD, module.TIMER_NEW))

    def test_unknown_source_fails_without_guessing(self):
        with self.assertRaises(ValueError):
            module.patch_text('xTimerStop(another_timer, 0);', module.TIMER_OLD, module.TIMER_NEW)

    def test_ambiguous_source_fails(self):
        with self.assertRaises(ValueError):
            module.patch_text(module.TIMER_OLD * 2, module.TIMER_OLD, module.TIMER_NEW)

    def test_public_reset_declaration_is_idempotent(self):
        result = module.patch_text(module.API_OLD, module.API_OLD, module.API_NEW)
        self.assertIn('void libpax_counter_reset();', result)
        self.assertEqual(result, module.patch_text(result, module.API_OLD, module.API_NEW))

class BleLifecycleTests(unittest.TestCase):
    def test_single_queue_consumer_and_failure_cleanup(self):
        import shutil
        import subprocess
        import tempfile
        compiler = shutil.which('c++')
        self.assertIsNotNone(compiler)
        harness = r'''
#include <cassert>
#include <cstddef>
#define pdPASS 1
#define LIBPAX_ARDUINO
#define BLE_ADV_QUEUE_SIZE 60
#define ESP_LOGE(...) ((void)0)
struct host_rcv_data_t { char bytes[258]; };
void *adv_queue=nullptr, *hci_eventprocessor=nullptr;
int ble_adv_dropped=0, queues=0, tasks=0, deletes=0, stops=0;
bool queueOk=true, taskOk=true;
void hci_evt_process(void*) {}
void *xQueueCreate(int, size_t) { ++queues; return queueOk ? (void*)1 : nullptr; }
int xTaskCreate(void (*)(void*),const char*,int,void*,int,void **out) {
 ++tasks; if (!taskOk) return 0; *out=(void*)2; return pdPASS;
}
void vQueueDelete(void*) { ++deletes; }
void btStop() { ++stops; }
void initialize() {
'''+module.BLE_NEW+r'''
}
int main() {
 for (int i=0;i<100;++i) initialize();
 assert(queues==1 && tasks==1 && deletes==0 && stops==0);
 adv_queue=nullptr; hci_eventprocessor=nullptr; queueOk=false;
 initialize(); assert(stops==1 && tasks==1 && deletes==0);
 queueOk=true; taskOk=false;
 initialize(); assert(stops==2 && deletes==1 && adv_queue==nullptr && hci_eventprocessor==nullptr);
 taskOk=true;
 initialize(); assert(adv_queue!=nullptr && hci_eventprocessor!=nullptr);
}
'''
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)
            (path/'ble.cpp').write_text(harness)
            subprocess.run([compiler,'-std=c++11','-Wall','-Wextra','-Werror',str(path/'ble.cpp'),'-o',str(path/'ble')],check=True,capture_output=True)
            subprocess.run([str(path/'ble')],check=True,capture_output=True)

    def test_ble_patch_idempotent_and_unknown_source_rejected(self):
        result=module.patch_text(module.BLE_OLD,module.BLE_OLD,module.BLE_NEW)
        self.assertEqual(result,module.patch_text(result,module.BLE_OLD,module.BLE_NEW))
        with self.assertRaises(ValueError):
            module.patch_text('unknown BLE implementation',module.BLE_OLD,module.BLE_NEW)


if __name__ == '__main__':
    unittest.main()
