# Research notes (20 Oct 2026)

What already exists, so the repo only builds what's missing. Everything here was checked on 20 Oct 2026; re-check before relying on version-specific details.

## FPP pixel output pins (M4): VERIFIED from source

Source: FalconChristmas/fpp `master` at commit db22d69 (20 Oct 2026).

| Kit output | FPP string | Pi header pin | BCM GPIO | DPI bit |
|---|---|---|---|---|
| Tree A | Output 1 | P1-12 | GPIO18 | DPI_D14 |
| Tree B | Output 2 | P1-35 | GPIO19 | DPI_D15 |

- Cape setting: **PiHat**, string driver **PiHat-DPIPixels** ("PiHat (DPIPixels - allows onboard audio)"). Pins from `capes/pi/PiHat-eeprom.bin` → `strings/PiHat-DPIPixels.json`; pin-to-DPI-bit mapping from `src/non-gpl/DPIPixels/DPIPixels.cpp` (`GetDPIPinBitPosition`, lines ~1027-1028: `P1-12 → DPI_D14 - GPIO18`, `P1-35 → DPI_D15 - GPIO19`).
- **No licence needed for two full-length strings.** `DPIPixels.cpp` lines ~271-276: if no licence, `licensedOutputs = 2` ("Two strings driven directly off the Pi's GPIO header is what the old RPIWS281X driver provided for free, so DPI has to keep providing it"). Outputs beyond the licensed count are clamped to 50 pixels. Added in commit e791964 (16 Jul 2026, "drop rpi_ws281x, migrate Pi string configs to DPIPixels ... two unlicensed outputs on every Pi"), so it's in FPP 10.1 (15 Sep 2026) and 10.2 (3 Oct 2026). The PiHat cape description text still says "50 pixels per string without a license key"; that text is out of date versus the code. **Bench check:** confirm a full 92-pixel string lights on output 2 with no licence.
- **Other GPIOs:** the FPP overlay (`dtoverlay=vc4-kms-dpi-fpp`, source `capes/drivers/pi/vc4-kms-dpi-fpp.dts`) claims no pins itself (`dpi_no_gpio`, empty `brcm,pins`). With a virtual EEPROM the driver muxes only the pins of configured ports (DPIPixels.cpp ~280-286). So a kit uses GPIO18 and GPIO19 only; I2C, SPI and the rest of the header stay free. Audio is the USB card, so the PCM/PWM roles of GPIO18/19 don't matter.
- The DPI overlay fixes the framebuffer at 1920 wide with a 38.4MHz pixel clock (KMS DPI required). Max 1600 pixels per string. **Bench check on the Pi 3 / 3 A+:** that the KMS DPI device comes up (FPP shows a warning if not).

## xLights custom models (M2)

- xLights has no import of node coordinates (CSV/SVG/DXF) for custom models. Options are the hand-edited grid, `.xmodel` import/export, and **Tools → Generate Custom Model**, which builds a model from a video of the real prop cycling its lights ([manual](https://manual.xlights.org/xlights/chapters/chapter-five-menus/tools/generate-custom-model)). Useful later to cross-check a finished tree, not to design one.
- A third-party GUI, David Peace's Custom Model Builder (lightshowhub.com), exists but is manual.
- **Conclusion:** our generator (layout JSON → `.xmodel` with a face definition) is not duplicated. The `.xmodel` XML format still has to be confirmed from the xLights source or a sample export.
- Commercial singing trees (Boscoyo/EFL coroplast, wire-frame trees) ship their own xmodels; useful as references for face definitions, not reusable for our layout.
- Lip-sync is built into xLights (lyrics → phoneme timing tracks, Faces effect; Papagayo import also works). The face definition in our model is what matters.

## Sequencing helpers

- [JohnBreault/xlights-mcp-server](https://github.com/JohnBreault/xlights-mcp-server) (MIT, beta, ~17 stars): MCP server that analyses an MP3 and writes `.xsq` sequences for the models in a show folder, imports community sequences, and has FPP tools (status, upload, playlists). Python 3.11+, uv, ffmpeg; optional ~2GB stem-separation models. Needs our models in the show folder first. Review its source before installing.

## Home Assistant (M7)

- [koolsb/ha-fpp](https://github.com/koolsb/ha-fpp) (HACS): FPP as a media player entity (current sequence/playlist, start/stop playlists, volume). Use this rather than writing our own.
- [carldanley/ha-fpp-mqtt](https://pkg.go.dev/github.com/carldanley/ha-fpp-mqtt): Go bridge exposing FPP overlay models as MQTT lights (last release v1.0.7, Mar 2024).
- FPP also has a REST API and native MQTT. Check maintenance status of ha-fpp before relying on it.

## xLights install

- Installed xLights 2026.18 on Rob's PC via `winget install xLightsSequencer.xLights` (20 Oct 2026), at `C:\Program Files\xLights`.

## Kit computer and pixel output options (20 Oct 2026)

Why: the Pi Zero 2 W is sold out (Pimoroni out of stock in Sep 2026; Raspberry Pi reports ~1M Zero-family units on back order, no official restock date). The kits currently plan Pi 3 A+ boards driving pixels straight off GPIO.

- **Pi 3 Model A+:** in stock at The Pi Hut, about £24 (PriceSpy from ~£22.86). Its original production guarantee ran to Jan 2023 and has expired, so buy all 6 now rather than later. Same SoC family as Rob's Pi 3, so a bench test on the Pi 3 is representative.
- **Pi 4 1GB:** still $35 list after the Dec 2025 RAM price rises; works with FPP and DPIPixels but needs a 3A supply and runs hotter. No real gain for 2 strings.
- **Pi 5 1GB:** launched Dec 2025 at $45; FPP supports DPIPixels on RP1. More cost and power than needed.
- **FPP 10 dropped the old rpi_ws281x driver** (commit e791964, Jul 2026). On FPP 10 the only way to drive pixels from Pi GPIO is DPIPixels, so the Pi 3 / A+ DPI path must be bench-tested before buying 6.
- **Direct GPIO through a 74AHCT125 is the standard approach,** not a hack: it's what FPP's own PiHat/PiCap configuration expects, with only GPIO18/19 used. The real risks are (1) DPI not coming up on the Pi 3 A+, and (2) ESD/surges on 3m outdoor data leads. Mitigation for (2): 33Ω series resistor at the buffer (planned) plus optionally a small TVS diode on each data line at the box.
- **ESP32 pixel controllers as an alternative for remote pairs:** e.g. QuinLED Dig-Uno (ESP32, 2 outputs, built-in 74AHCT level shifting, 5/12/24V input, ships with WLED). FPP can stream DDP to it over Wi-Fi; 552 channels per kit is tiny. Community reports say Wi-Fi streaming can lag or jitter, which matters for lip-sync; ESPixelStick firmware has an FPP Remote mode (sequence on the ESP's SD card, sync packets only) that avoids that, but needs an SD-equipped ESP32 and may need compiling. ESPs have no audio, so every site still needs one FPP Pi as master.
