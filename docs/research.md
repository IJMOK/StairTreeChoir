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
