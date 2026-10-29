"""Exercise the actual saveConfig body with a failure-injectable NVS fake."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class ConfigSaveTests(unittest.TestCase):
    def test_nvs_failures_and_exact_write_length(self):
        compiler = shutil.which('c++')
        self.assertIsNotNone(compiler, 'host C++ compiler is required')
        source = (Path(__file__).parents[1] / 'src/configmanager.cpp').read_text()
        body = source.split('bool saveConfig(bool erase) {', 1)[1].split('// load configuration', 1)[0]
        harness = r'''
#include <cassert>
#include <cstring>
#include <cstddef>
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGE(...) ((void)0)
#define TAG "test"
#define DEVCONFIG "paxcntcfg"
struct Fake {
 bool opens=true, clears=true;
 size_t writes=5;
 int ended=0, puts=0, clearCalls=0;
 bool begin(const char*, bool) { return opens; }
 bool clear() { ++clearCalls; return clears; }
 size_t putBytes(const char*, const void*, size_t) { ++puts; return writes; }
 void end() { ++ended; }
} nvram;
int cfg=42;
const unsigned char cfgMagicBytes[]={7};
const size_t cfgLen=sizeof(cfg), cfgLen2=sizeof(cfgMagicBytes);
unsigned char buffer[cfgLen+cfgLen2];
void defaultConfig(int *value) { *value=0; }
'''
        harness += 'bool saveConfig(bool erase) {' + body
        harness += r'''
int main() {
 nvram.opens=false;
 assert(!saveConfig(false)); assert(nvram.puts==0); assert(nvram.ended==0);
 nvram=Fake{}; nvram.clears=false;
 assert(!saveConfig(true)); assert(nvram.puts==0); assert(nvram.ended==1); assert(cfg==42);
 nvram=Fake{}; nvram.writes=0;
 assert(!saveConfig(false)); assert(nvram.ended==1);
 nvram=Fake{}; nvram.writes=cfgLen+cfgLen2-1;
 assert(!saveConfig(false)); assert(nvram.ended==1);
 nvram=Fake{}; nvram.writes=cfgLen+cfgLen2;
 assert(saveConfig(false)); assert(nvram.ended==1); assert(nvram.clearCalls==0);
 assert(std::memcmp(buffer,&cfg,cfgLen)==0);
 assert(buffer[cfgLen]==7);
 nvram=Fake{}; nvram.writes=cfgLen+cfgLen2;
 assert(saveConfig(true)); assert(cfg==0); assert(nvram.clearCalls==1); assert(nvram.ended==1);
}
'''
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path / 'save.cpp').write_text(harness)
            subprocess.run([compiler, '-std=c++11', '-Wall', '-Wextra', '-Werror', str(path / 'save.cpp'), '-o', str(path / 'save')], check=True, capture_output=True)
            subprocess.run([str(path / 'save')], check=True, capture_output=True)


if __name__ == '__main__':
    unittest.main()
