#include "cardputer.h"
#include <cassert>

int main() {
  CardputerSettings saved{-80, true, true};
  auto draft = saved;
  draft.adjustRssi(-5);
  assert(draft.rssi == -85);
  draft.adjustRssi(-1000);
  assert(draft.rssi == -120);
  draft.adjustRssi(1000);
  assert(draft.rssi == 0);
  // Editing and cancelling must not mutate the live settings.
  draft.wifi = false;
  draft.ble = false;
  assert(saved.rssi == -80 && saved.wifi && saved.ble);
  draft = saved;
  assert(draft.rssi == -80 && draft.wifi && draft.ble);
  // Commit copies all three settings, including independently disabled radios.
  draft.adjustRssi(5);
  draft.ble = false;
  saved = draft;
  assert(saved.rssi == -75 && saved.wifi && !saved.ble);
}
