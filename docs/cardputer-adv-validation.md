# Cardputer ADV development validation

Updated: 2026-10-29. Host build/tests have passed. The user has confirmed that the firmware runs and that the display flicker is resolved. Other device checks remain open.

The implementation and helper scripts are on the `cardputer-adv` branch. Switch to that branch before running the following commands.

## Build and test commands

```sh
git switch cardputer-adv
pio run -c platformio_cardputer.ini -e cardputer-adv
python3 -m unittest discover -s tests -v
c++ -std=c++11 -Wall -Wextra -Werror -Iinclude tests/cardputer_settings_test.cpp -o /tmp/pax-cardputer-settings-test
/tmp/pax-cardputer-settings-test
python3 scripts/package-cardputer.py --partition-table ~/.platformio/packages/framework-arduinoespressif32/tools/partitions/default_8MB.csv
```

The default package directory is `dist/cardputer-adv`, containing an application-only binary, `SHA256SUMS`, and `manifest.json`. Use `--output` for a separate revision directory. The manifest records exact size, checksum, and source state at packaging time; a rebuild can have a different checksum due to build metadata.

Direct dependencies are pinned in `platformio_cardputer.ini`. `scripts/patch_libpax.py` applies checked patches to the pinned libpax revision, releases the report timer on stop, exposes the existing reset API, and reuses a single BLE queue/consumer across restarts. Unknown source patterns stop the build. The BLE queue and task intentionally remain allocated while paused. Upstream BLE initialization errors are not fully propagated to the caller, so actual scan operation must be checked on the device.

## Controls and behavior

- Space pauses/resumes; resume starts a new counting window.
- C clears counts; S opens settings.
- Physical `; . , /` keys navigate; Fn arrows use the same positions.
- Enter saves/applies; backtick/Esc position discards the draft.
- Settings: RSSI threshold, Wi-Fi enable, BLE enable. Applying settings starts a new window.
- Main pages show separate counts and status. Counts are cumulative between clears/restarts.

The base build has no LoRa transmission, GNSS, SD logging, or OTA.

## Device acceptance

- [x] User ran the development firmware on ADV and observed its display.
- [x] User confirmed v0.1.1 displays normally without flicker on 2026-10-29.
- [ ] Record Launcher version, actual partition layout, and available application capacity.
- [ ] Verify switching back to other installed firmware.
- [ ] Verify keyboard controls and Wi-Fi-only, BLE-only, and combined scan operation.
- [ ] Exercise repeated pause/resume and clear operations without persistent heap loss or resets.
- [ ] Change settings, save, observe scan behavior, reboot, and verify persistence; cancel must not save.

These unchecked items are not inferred from the user's confirmation of the display fix.

## Delivered artifacts

Both files were copied to the ADV SD `bin` directory, synchronized, and read back byte-for-byte. The volume was safely ejected. Flash installation was performed by the user, not by the host copy operation.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `paxcounter-adv-v0.1.0-dev.bin` | 974080 | `f896d8d09d9032075437852578cb3d246dcab3ed6a8971bde842299f0c4e30d0` |
| `paxcounter-adv-v0.1.1-flickerfix.bin` | 979440 | `7599c508d87f2925bfb0332d56c4f9c89fc5b55b9568db71105a4b310416e0ac` |

The v0.1.1 build reports 64,984 bytes of static RAM usage. Runtime allocations, including the canvas, are additional.

## Flicker defect: verified fixed

The first build cleared the physical LCD every 250 ms before drawing individual text elements, exposing intermediate black frames. The fix renders into a 240×135, 8-bit canvas and then calls `pushSprite`. The canvas requires approximately 32,400 bytes of runtime storage. Allocation failure displays an error and prevents UI task startup.

`tests/test_cardputer_render.py` compiles the actual draw function against an instrumented surface. It failed on the original visible-panel clearing path and passed after the change across the count, settings, and status pages. The user subsequently confirmed that flicker was gone.

Artifact revision v0.1.1 retains `PROGVERSION=0.1.0` because upstream uses that value for configuration migration. This display-only revision preserves the configuration layout and avoids resetting saved settings.
