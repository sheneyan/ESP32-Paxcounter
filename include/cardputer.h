#pragma once
#include <stdint.h>

// Plain state: edit a copy, commit only after successful apply and persistence.
struct CardputerSettings {
  int16_t rssi;
  bool wifi;
  bool ble;
  void adjustRssi(int delta) {
    int value = rssi + delta;
    rssi = value < -120 ? -120 : (value > 0 ? 0 : value);
  }
};

#ifdef CARDPUTER_ADV
void cardputer_init();
#endif
