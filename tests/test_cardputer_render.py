import pathlib, subprocess, tempfile, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
class RenderTests(unittest.TestCase):
    def test_redraw_never_clears_visible_panel(self):
        source = (ROOT / 'src/cardputer.cpp').read_text()
        draw = source[source.index('void draw() {'):source.index('void uiTask(')]
        harness = r'''
#include <cassert>
#include <cstdint>
#define TFT_BLACK 0
#define TFT_WHITE 1
#define TFT_CYAN 2
#define TFT_YELLOW 3
struct Surface {
 int clears=0, pushes=0;
 void startWrite(){} void endWrite(){}
 template<class... T> void fillScreen(T...){++clears;}
 template<class... T> void setTextSize(T...){}
 template<class... T> void setTextColor(T...){}
 template<class... T> void setCursor(T...){}
 template<class... T> void printf(T...){}
 template<class... T> void print(T...){}
 template<class... T> void fillRect(T...){}
 void pushSprite(int,int){++pushes;}
};
struct { Surface Display; } M5Cardputer;
Surface frame;
bool paused=false, editing=false;
int page=0, selection=0;
struct {int rssi=-80; bool wifi=true,ble=true;} draft;
struct {int rssilimit=-80,wifiscan=1,blescan=1;} cfg;
struct {unsigned wifi_count=5,ble_count=3;} visible;
const char* notice="Saved";
uint32_t noticeUntil=1000;
uint32_t millis(){return 500;}
struct {unsigned getFreeHeap(){return 100000;}} ESP;
'''
        harness += draw + r'''
int main(){
 for(int i=0;i<3;++i){editing=i==1;page=i==2;draw();}
 assert(M5Cardputer.Display.clears==0);
 assert(frame.pushes==3);
}
'''
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td); (p/'test.cpp').write_text(harness)
            subprocess.run(['c++','-std=c++11',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
            subprocess.run([str(p/'test')],check=True)
