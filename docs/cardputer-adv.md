# Cardputer ADV adaptation roadmap

Updated: 2026-10-29. The initial software build is complete. The user has confirmed that the development firmware runs and that the display no longer flickers after the v0.1.1 fix. Remaining acceptance work is tracked in the [validation record](cardputer-adv-validation.md).

## Direction

Retain the upstream fork history, counting core, configuration storage, and scheduling. Add a dedicated ADV target and UI while keeping the base firmware small enough for practical M5Launcher use. Enable optional subsystems only when needed.

| Stage | Scope | Acceptance evidence |
| --- | --- | --- |
| Base counter | ADV build, Wi-Fi/BLE counting, display, keyboard, settings | Build plus device checks of counts, controls, save/apply, and persistence |
| Launcher delivery | Application-only image and size metadata | Launcher version, actual partition capacity, installation and switching results |
| Optional extensions | Trends, GNSS, statistical CSV, LoRaWAN | Separate evidence for each enabled feature |

The base build disables OTA, LoRaWAN, GNSS, SD logging, MQTT, and unrelated sensors. It includes only the libraries required by the current source dependency graph; header dependencies may still require libraries for disabled peripherals.

## Hardware reference

The following mappings come from official documentation and upstream code. They are reference inputs, not proof that this fork has tested the Cap:

- Upstream S3/SX1262 starting points: `platformio_orig_s3.ini`, `shared/hal/heltecv3.h`, and `shared/hal/ttgot3s3.h`.
- ADV display: 240×135 pixels; keyboard support must target ADV specifically.
- Cap LoRa-1262: SCK=G40, MISO=G39, MOSI=G14, NSS=G5, RST=G3, IRQ=G4, BUSY=G6.
- The newer Cap requires PI4IOE5V6408 P0 to enable the RF antenna switch. TCXO and DIO2 configuration must also be checked.
- GNSS: ADV RX=G15, TX=G13; documented UART default is 115200 baud with NMEA output.
- Shared SD/LoRa bus access needs arbitration and combined-operation testing.
- The documented Cap band is 868–923 MHz. Match LoRaWAN gateway and regional settings rather than blindly retaining upstream EU868 defaults.

References: [ADV](https://docs.m5stack.com/en/core/Cardputer-Adv), [Cap](https://docs.m5stack.com/en/cap/Cap_LoRa-1262), [upstream S3 configuration](https://github.com/cyberman54/ESP32-Paxcounter/blob/master/platformio_orig_s3.ini).

## Delivery requirements

Record the source revision and working-tree state, dependency versions, build command, application size, SHA-256, and partition requirements. Record Launcher version and actual device behavior separately. Copying a binary onto SD is staging; installation, boot, controls, and firmware switching require their own evidence.

The user's third-party Cap previously ran official M5Stack Meshtastic firmware, reportedly around 2.7.22. A matching 2.7.22 image was found on the SD card, which confirms file presence rather than the installed version. GNSS and this fork's radio behavior remain unverified.

## Boundaries and remaining work

Counts represent devices and trends, not accurate headcounts. Do not add cross-protocol identity matching, raw MAC archives, individual trajectories, or de-randomization.

LoRaWAN is the planned transport inherited from upstream. Raw LoRa point-to-point, full map navigation, and Meshtastic protocol support are outside the current scope.

Remaining checks include scan behavior, repeated pause/resume and clear operations, settings persistence, long-run memory use, Launcher coexistence, and battery life. Future extensions require their own radio, GNSS, and SD concurrency verification.
