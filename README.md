# ESP32-Paxcounter for Cardputer ADV

A lightweight adaptation of [ESP32-Paxcounter](https://github.com/cyberman54/ESP32-Paxcounter) for **M5Stack Cardputer ADV**, with planned Cap LoRa-1262 support. The goal is a portable Wi-Fi/BLE device counter that fits comfortably alongside other firmware in M5Launcher.

**Status:** The initial ADV build, display, keyboard controls, and settings storage are implemented. The user has booted the development firmware and confirmed that the v0.1.1 display fix eliminates flicker. Scan accuracy, repeated control operations, settings persistence after reboot, and switching between installed firmware still need explicit device verification. LoRaWAN, GNSS, SD logging, MQTT, and OTA are disabled in this build.

## Hardware and scope

| Hardware | Role |
| --- | --- |
| Cardputer ADV, ESP32-S3, 8 MB flash | Wi-Fi/BLE scanning, 240×135 display, keyboard |
| Cap LoRa-1262, SX1262 + GNSS | Planned LoRaWAN and positioning support |
| microSD card | Launcher application storage; statistical logging planned |

The connected third-party Cap has previously worked with the official M5Stack Meshtastic firmware according to the user. That evidence does not establish LoRaWAN or GNSS operation in this fork.

References: [Cardputer ADV](https://docs.m5stack.com/en/core/Cardputer-Adv), [Cap LoRa-1262](https://docs.m5stack.com/en/cap/Cap_LoRa-1262).

## Build

Install PlatformIO Core, then run:

```sh
pio run -c platformio_cardputer.ini -e cardputer-adv
```

This dedicated target needs no OTA or LoRaWAN credentials. It retains upstream counting and configuration code, with an ADV-specific UI and checked compatibility patches for the pinned libpax revision.

The application image is `.pio/build/cardputer-adv/firmware.bin`. The tested v0.1.1 artifact is **979,440 bytes** (about 956 KiB). Its build partition table is not evidence of the device's current Launcher layout. Install the application image through Launcher; do not replace the bootloader or partition table with this application file.

See [validation and packaging](docs/cardputer-adv-validation.md) for commands, checksums, and device-test status.

## Controls

| Key | Action |
| --- | --- |
| Space | Pause/resume; resume starts a new counting window |
| C | Clear counts |
| S | Open settings |
| `;` / `.` | Select a setting |
| `,` / `/` | Adjust a setting or change the main page |
| Enter | Apply and save |
| Backtick / Esc key position | Cancel editing |

Settings include RSSI threshold and independent Wi-Fi/BLE switches. Applying settings starts a new counting window. Counts accumulate until cleared or restarted. The English UI uses an 8-bit off-screen canvas to avoid exposing intermediate blank frames.

## What the numbers mean

The firmware counts detected wireless devices, not people. Wi-Fi and BLE totals cannot simply be added to obtain a headcount. MAC randomization, radio state, signal strength, and the environment affect the observations.

This fork keeps aggregate counting as its scope. It does not add persistent raw MAC storage, individual tracking, or address de-randomization.

## Roadmap

1. Complete device verification of the base counter and controls.
2. Measure Launcher installation, available application space, and switching behavior.
3. Add trend views, GNSS, statistical CSV logging, and LoRaWAN separately as needed.

See the [adaptation roadmap](docs/cardputer-adv.md). Firmware size, partition capacity, and Launcher storage behavior are separate measurements; a smaller binary alone does not prove that other firmware never needs to be removed.

## Upstream and licensing

- [This fork](https://github.com/sheneyan/ESP32-Paxcounter)
- [Upstream repository](https://github.com/cyberman54/ESP32-Paxcounter)
- [Preserved upstream README](README.upstream.md)
- [Upstream documentation](https://paxcounter.org/)

Upstream copyright, license notices, and credits are preserved. The main project uses Apache License 2.0; some files have separate notices. See [LICENSE](LICENSE), [upstream credits](README.upstream.md#credits), and individual source headers. Upstream documentation describes the general project and does not establish ADV validation for this fork.
