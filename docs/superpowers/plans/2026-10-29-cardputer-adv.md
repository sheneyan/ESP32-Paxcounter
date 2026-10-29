# Cardputer ADV initial implementation plan and progress

**Goal:** Provide a lightweight Wi-Fi/BLE counter with ADV display, keyboard controls, persistent settings, and an application image suitable for Launcher testing.

**Architecture:** Keep upstream main, libpax, configuration management, and scheduling. Add a dedicated build configuration, HAL, and UI task. Disable optional transport and sensor features in the base build.

**Stack:** PlatformIO, ESP32 Arduino, libpax, M5Cardputer, M5Unified, and M5GFX.

## Build target

- [x] Add `platformio_cardputer.ini`, `shared/hal/cardputer_adv.h`, and `shared/cardputer.conf` for ESP32-S3, 8 MB flash, and no PSRAM.
- [x] Avoid upstream `shared/build.py`, which hardcodes `platformio.ini` and requires OTA/LoRaWAN credentials even for the base target.
- [x] Pin direct dependencies and build without private key files.
- [x] Disable OTA, LoRaWAN, GNSS, SD logging, MQTT, and unrelated sensors.

Command: `pio run -c platformio_cardputer.ini -e cardputer-adv`.

## Display and keyboard

- [x] Add `include/cardputer.h` and `src/cardputer.cpp`, with a guarded startup hook in `src/main.cpp`.
- [x] Use the ADV-compatible M5Cardputer 1.1.1 API; keep the legacy display backend unchanged.
- [x] Show separate Wi-Fi/BLE counts, scan state, RSSI threshold, and a status page.
- [x] Process keyboard input and display refresh in one UI task; refresh at 4 Hz.
- [x] Add pause/resume, clear, page selection, and settings editing. Resume starts a new window.
- [x] Replace direct LCD clearing with an 8-bit off-screen frame; user confirmed the flicker fix.

## Settings and lifecycle

- [x] Edit a draft of RSSI/Wi-Fi/BLE settings; Enter applies/saves and Esc discards.
- [x] Make `saveConfig` return actual NVS success, including complete-write checks.
- [x] Add failure rollback in the UI rather than reporting a failed operation as saved.
- [x] Expose libpax's existing counter reset instead of using upstream's deprecated no-op reset command.
- [x] Add checked libpax patches for report-timer disposal and persistent BLE queue/consumer reuse.
- [x] Add host checks for draft boundaries, NVS failures, patch idempotence, repeated BLE initialization, and draw behavior.
- [ ] Verify save/apply/cancel and persistence after reboot on the device.
- [ ] Verify repeated pause/resume and clear operation with stable runtime memory.

## Packaging and acceptance

- [x] Add `scripts/package-cardputer.py` for application-only validation, SHA-256, source state, and optional build-partition evidence.
- [x] Reject bootloader/merged images and images exceeding all supplied application slots.
- [x] Copy the two development revisions to SD and verify their bytes.
- [x] Record user-confirmed display operation and flicker resolution.
- [ ] Record Launcher version, current partitions, and switching behavior.
- [ ] Verify Wi-Fi-only, BLE-only, and combined scan behavior.

See [validation record](../../cardputer-adv-validation.md) for commands, artifact checksums, and remaining acceptance items.

## Hardware evidence and future scope

The host identified an ESP32-S3 USB serial device. The user reported successful Mesh use with a third-party Cap and official M5Stack firmware around 2.7.22; a matching image was found on SD. This is a hardware reference, not proof of this fork's LoRaWAN or GNSS operation.

Future Cap work should verify SX1262 pin mapping, antenna switch, TCXO, and radio settings against the known-working configuration. LoRaWAN joining, GNSS, and shared SD/LoRa access require separate implementation and acceptance.
