#ifdef CARDPUTER_ADV
#include "cardputer.h"
#include "configmanager.h"
#include "libpax_helpers.h"
#include "irqhandler.h"
#include <M5Cardputer.h>

namespace {
M5Canvas frame(&M5Cardputer.Display);
bool paused = false;
bool editing = false;
uint8_t page = 0;
uint8_t selection = 0;
CardputerSettings draft{};
count_payload_t visible{};
const char *notice = "";
uint32_t noticeUntil = 0;

void message(const char *text) {
  notice = text;
  noticeUntil = millis() + 4000;
}

bool startCounter() {
  if (libpax_counter_init(setSendIRQ, &count_from_libpax,
                         cfg.sendcycle * 2, cfg.countermode) != 0)
    return false;
  if (libpax_counter_start() == 0)
    return true;
  libpax_counter_stop();
  return false;
}

void togglePause() {
  if (!paused) {
    libpax_counter_count(&visible);
    if (libpax_counter_stop() != 0) {
      message("Pause failed");
      return;
    }
    paused = true;
  } else {
    if (!startCounter()) {
      message("Resume failed");
      return;
    }
    paused = false;
    visible = {};
    message("New counting window");
  }
}

void applySettings() {
  libpax_config_t previous;
  libpax_get_current_config(&previous);
  auto candidate = previous;
  candidate.wificounter = draft.wifi;
  candidate.blecounter = draft.ble;
  candidate.wifi_rssi_threshold = draft.rssi;
  candidate.ble_rssi_threshold = draft.rssi;
  const auto oldCfg = cfg;
  const bool wasPaused = paused;
  if (!wasPaused && libpax_counter_stop() != 0) {
    message("Cannot stop scan");
    return;
  }
  paused = true;
  if (libpax_update_config(&candidate) != 0) {
    libpax_update_config(&previous);
    if (!wasPaused) paused = !startCounter();
    message("Apply failed");
    return;
  }
  cfg.rssilimit = draft.rssi;
  cfg.wifiscan = draft.wifi;
  cfg.blescan = draft.ble;
  if ((!wasPaused && !startCounter()) || !saveConfig(false)) {
    // Roll back live state as well as the draft; do not report a failed save as success.
    libpax_counter_stop();
    cfg = oldCfg;
    libpax_update_config(&previous);
    paused = wasPaused || !startCounter();
    message("Save/apply failed");
    return;
  }
  paused = wasPaused;
  visible = {};
  editing = false;
  message("Settings saved");
}

void handleKey() {
  auto &keys = M5Cardputer.Keyboard.keysState();
  auto pressed = [](char c) { return M5Cardputer.Keyboard.isKeyPressed(c); };
  if (editing) {
    if (pressed('`')) {
      editing = false;
      message("Changes discarded");
    } else if (keys.enter) {
      applySettings();
    } else if (pressed(';')) {
      selection = (selection + 2) % 3;
    } else if (pressed('.')) {
      selection = (selection + 1) % 3;
    } else if (pressed(',') || pressed('/')) {
      if (selection == 0)
        draft.adjustRssi((pressed(',')) ? -5 : 5);
      else if (selection == 1)
        draft.wifi = !draft.wifi;
      else
        draft.ble = !draft.ble;
    }
    return;
  }
  if (pressed('s') || pressed('S')) {
    draft = {cfg.rssilimit, bool(cfg.wifiscan), bool(cfg.blescan)};
    editing = true;
    selection = 0;
  } else if (keys.space) {
    togglePause();
  } else if (pressed('c') || pressed('C')) {
    libpax_counter_reset();
    visible = {};
    message("Counts cleared");
  } else if (pressed(',') || pressed('/')) {
    page ^= 1;
  }
}

void draw() {
  auto &d = frame;
  d.startWrite();
  d.fillScreen(TFT_BLACK);
  d.setTextSize(1);
  d.setTextColor(TFT_CYAN, TFT_BLACK);
  d.setCursor(4, 3);
  d.printf("Paxcounter ADV  %s", paused ? "PAUSED" : "SCANNING");
  d.setTextColor(TFT_WHITE, TFT_BLACK);
  if (editing) {
    d.setCursor(4, 24);
    d.printf("%c RSSI: %d dBm\n", selection == 0 ? '>' : ' ', draft.rssi);
    d.setCursor(4, 43);
    d.printf("%c Wi-Fi: %s", selection == 1 ? '>' : ' ', draft.wifi ? "ON" : "OFF");
    d.setCursor(4, 62);
    d.printf("%c BLE: %s", selection == 2 ? '>' : ' ', draft.ble ? "ON" : "OFF");
    d.setCursor(4, 88);
    d.print("Arrows: edit  Enter: save");
    d.setCursor(4, 100);
    d.print("Esc/`: cancel");
  } else if (page == 0) {
    d.setTextSize(2);
    d.setCursor(4, 28);
    d.printf("WiFi: %lu", (unsigned long)visible.wifi_count);
    d.setCursor(4, 54);
    d.printf("BLE : %lu", (unsigned long)visible.ble_count);
    d.setTextSize(1);
    d.setCursor(4, 82);
    d.printf("RSSI %d dBm  Cumulative", cfg.rssilimit);
    d.setCursor(4, 99);
    d.print("Space:pause C:clear S:settings");
    d.setCursor(4, 110);
    d.print(", / : page   Devices, not people");
  } else {
    d.setCursor(4, 27);
    d.printf("Wi-Fi %s / BLE %s", cfg.wifiscan ? "ON" : "OFF", cfg.blescan ? "ON" : "OFF");
    d.setCursor(4, 45);
    d.printf("Free heap: %lu", (unsigned long)ESP.getFreeHeap());
    d.setCursor(4, 63);
    d.printf("Uptime: %lus", (unsigned long)(millis()/1000));
    d.setCursor(4, 81);
    d.print("Resume starts a new window.");
    d.setCursor(4, 101);
    d.print("Space:pause C:clear S:settings");
  }
  if (int32_t(noticeUntil - millis()) > 0) {
    d.fillRect(0, 122, 240, 13, TFT_BLACK);
    d.setCursor(4, 124);
    d.setTextColor(TFT_YELLOW, TFT_BLACK);
    d.print(notice);
  }
  d.endWrite();
  frame.pushSprite(0, 0);
}

void uiTask(void *) {
  uint32_t nextFrame = 0;
  // Process only new key presses, not key releases; avoid isChange's key-count-only semantics.
  uint64_t previous = 0;
  for (;;) {
    M5Cardputer.update();
    uint64_t current = 0;
    for (const auto &key : M5Cardputer.Keyboard.keyList())
      if (key.x >= 0 && key.x < 14 && key.y >= 0 && key.y < 4)
        current |= uint64_t(1) << (key.y * 14 + key.x);
    if (current & ~previous) handleKey();
    previous = current;
    if (int32_t(millis() - nextFrame) >= 0) {
      if (!paused) libpax_counter_count(&visible);
      draw();
      nextFrame = millis() + 250;
    }
    vTaskDelay(pdMS_TO_TICKS(20));
  }
}
} // namespace

void cardputer_init() {
  auto config = M5.config();
  config.internal_spk = false;
  config.internal_mic = false;
  M5Cardputer.begin(config, true);
  M5Cardputer.Display.setRotation(1);
  M5Cardputer.Display.setBrightness(100);
  // Compose the whole frame off-screen: clearing the physical LCD at 4 Hz
  // exposes a black frame between text draws. RGB332 needs only 32,400 bytes.
  frame.setPsram(false);
  frame.setColorDepth(8);
  if (!frame.createSprite(240, 135)) {
    M5Cardputer.Display.fillScreen(TFT_BLACK);
    M5Cardputer.Display.setCursor(0, 0);
    M5Cardputer.Display.print("Display buffer allocation failed");
    return;
  }
  const BaseType_t result = xTaskCreatePinnedToCore(uiTask, "cardputer-ui", 6144,
                                                  nullptr, 1, nullptr, 1);
  if (result != pdPASS) {
    M5Cardputer.Display.fillScreen(TFT_BLACK);
    M5Cardputer.Display.setCursor(0, 0);
    M5Cardputer.Display.print("UI task allocation failed");
    ESP_LOGE(TAG, "Cardputer UI task allocation failed");
  }
}
#endif
