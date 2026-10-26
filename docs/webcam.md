# Show webcam

A camera in the farmer's hedge across the road streams the Site A shows live to the village, family and friends. The same footage is also cut into clips to post afterwards. This is separate from the tree build and not needed for 1 Dec. This page holds the scope and BOM; nothing is built yet (24 Oct 2026).

## Scope

- **Live:** the shows only, from about 5 minutes before each show to a minute or two after. That's 17:00, 18:00, 19:00 and 20:00 (11–14 min each), plus the specials in [specials.md](specials.md): Saturday 18:00, NYE countdown, NYD. The waiting loop and announcements between shows are not streamed.
- **Clips:** every show is recorded with full, unmuted audio. Clips per song and per skit are posted afterwards (see [Clips](#clips)).

## Constraints

- The hedge is about **20 m** from the house with a clear view. It has **no power and no WiFi**, and it belongs to the farmer.
- The internet is the Huawei B818 4G hub, with unlimited data.
- Budget about £150–200. An earlier draft with a point-to-point link and a 100 Ah battery came to £560+ and was turned down.

## Design

```
[hedge]  WiFi camera (12V) <- MOSFET <- ESP32 (deep sleep) <- 3A fuse <- 12V 20Ah LiFePO4   (one box at the foot of a stake)
             ~~~ 2.4 GHz WiFi, ~20 m open air ~~~
[garden] Site A Cudy WR3000 (outdoors at the site box) -> home LAN
         Site A Pi 5 (FPP; see the note below): ffmpeg takes the camera's RTSP feed (video copied) + FPP's own audio
                            -> YouTube Live (auto-muted, see below)  and  -> local recording (full audio)
```

**Network.** No bridge is needed. The Site A router is already outdoors in the front garden, so the camera joins its WiFi across about 20 m of open air. If the signal at the hedge is weak, a directional antenna on the Cudy (about £10) fixes it.

**Camera.** A cheap outdoor WiFi camera, for example a Tapo C320WS/C325WB (ColorPro, good in the dark) or a Reolink RLC-510WA. Before ordering, check that it:
- has RTSP output
- runs on 12V DC
- can switch IR off (otherwise the hedge leaves flare)
- lets you lower the exposure if possible (otherwise the pixels blow out)

At 20 m, a fixed lens of about 4–6 mm frames the house front, so no zoom is needed. Turn the camera mic off. The stream takes clean sound from FPP, and passers-by aren't recorded.

### Power control: ESP32 with deep sleep

An ESPHome ESP32 switches the camera through a logic-level MOSFET and measures the battery through a voltage divider. It is one of the spare DevKitC-32U boards (10 bought, 6 needed for December), powered by a spare Mini560.

It sleeps between shows, which is what makes it better than a timer here:
- It wakes about 6 minutes before each show and switches the camera on. The camera needs about a minute to boot and join WiFi.
- While awake it syncs its clock, reports the battery voltage to HA, and fetches the next on/off times.
- It switches the camera off a minute or two after the show ends, then deep-sleeps until the next wake.

Where the schedule comes from: it is generated from the FPP schedule (`tools/gen_site_config.py`), so the specials, NYE and NYD are included. It is baked into the ESPHome config as the default, and HA can override it on each wake (for example "skip tonight", or "on now").

**Fail-safes:**
- **Maximum on-time.** A hard maximum on-time of 1 h per wake, except the NYE countdown, so a hung ESP or missed command can't drain the battery.
- **No WiFi.** If WiFi is down on wake, it falls back to the baked-in schedule.
- **Manual override.** A switch in the box bypasses the MOSFET for testing.

### Power budget

| | |
|---|---|
| Camera, IR off, ~4 W × ~1¾ h a night | ~7 Wh |
| ESP32 awake while the camera is on, plus deep sleep (DevKitC regulator/USB chip and Mini560 idle, ~10 mA) | ~1.5 Wh |
| **Per night** | **~9 Wh** |
| 12V 20 Ah LiFePO4 | 256 Wh, ~200 Wh usable |
| **Runtime** | **~3 weeks per charge**, about 2 charges a season; charge it indoors at home |

Saturday specials and the NYE countdown run longer; they add a few Wh each. No solar: December yield is poor, LiFePO4 must not charge below 0°C, and a panel on the hedge invites theft.

For comparison, a plain 12V timer can't follow the specials. With one window of about 16:50–20:20 it uses ~14 Wh a night (~2 weeks per charge), with no battery reading. An ESP32 that stays awake on WiFi uses ~17 Wh a night.

### Stream and recording

- **Note (Rob, 26 Oct 2026):** Site A's player is now the Pi 3, which is too slow to relay as well. Before the webcam goes ahead: either swap the Pi 5 back in as the Site A player, or run the relay on the Pi 5 beside it with FPP's audio sent across the network. Undecided.
- **Relay process.** ffmpeg runs on the Site A Pi 5 at low priority (`nice`) and copies the video, so the Pi never transcodes. Audio comes from FPP's own output through an ALSA loopback and is encoded to AAC. A one-off `-itsoffset` cancels the camera's ~1–2 s delay.
- **Start and stop.** The relay starts at the camera's on-time and stops after each show, following the same schedule as the ESP32.
- **Live.** The stream goes to YouTube Live with one persistent stream key and auto-start/stop, so each show becomes its own live video. The channel's `/live` link always points at whichever is on, so one link serves the whole season for family and the village Facebook group. About 720p–1080p at 2.5–4 Mbps, roughly 4 GB a night.
- **Recording.** The same ffmpeg also writes each show to disk with the **unmuted** audio, about 2 GB per show, on a USB stick on the Pi. They're copied to the PC each night.
- **Fallback.** If the relay ever disturbs FPP timing, move it to a separate Pi with one of the spare USB sound cards on a split of the amp input.

## Clips

FPP knows when each sequence starts and ends. A small tool (to write) reads that log and cuts each night's recording into one clip per song and per skit, named after the sequence. Picking the best ones to post is a manual job.

Where to post:
- **YouTube Shorts, Instagram Reels, TikTok** using the app's own licensed music library: post the clip with the song added from the app, lined up with the trees by hand. That's the legitimate way to post the commercial songs. Which songs are in each library varies.
- **Ordinary YouTube uploads** with the original audio: copyrighted songs usually get *claimed* (the rights holder takes the ads), not blocked or given a strike. That's far more forgiving than live.
- **Skits, Auld Lang Syne and any public-domain carols:** post as-is, with no music issue.

## BOM

UK prices are rough; check them when ordering.

| Qty | Item | Notes | Est. £ |
|---|---|---|---|
| 1 | Outdoor WiFi camera: RTSP, 12V input, colour night vision | e.g. Tapo C320WS/C325WB or Reolink RLC-510WA | 35–65 |
| 1 | 12V 20 Ah LiFePO4 battery | | 55–75 |
| 1 | 14.6V LiFePO4 charger | Mains, used at home | 20 |
| 1 | Logic-level MOSFET module (e.g. IRLZ44N/AO3400 board), divider resistors (e.g. 100k/22k), small toggle switch | ESP32 DevKitC-32U and Mini560 from the tree spares | 5 |
| 1 | Inline fuse holder | 3A blade fuse from stock | 3 |
| 1 | Box for the battery and electronics: an ammo box, or printed from `enclosure/sealed-box.scad` | Spare PG7 gland for the camera lead | 0–10 |
| 1 | Stake or post, or a clamp on an existing hedge stake, plus band clamps | Camera at about 2 m | 10–15 |
| 1 | Cable lock + camo tape | | 10 |
| 1 | USB stick, 64 GB+ | Show recordings on the Pi | 8 |
| – | Site A Pi 5 (FPP), Cudy site router, ESP32 + Mini560 | Already owned or planned | 0 |
| | **Total** | | **≈ £145–210** |
| opt | Directional 2.4 GHz antenna for the Cudy | Only if the signal at the hedge is weak | 10 |

## Music copyright

YouTube Content ID (and Facebook's Rights Manager) matches **recordings**. A carol that is out of copyright still gets flagged if the recording is a modern one. A match on a live stream can mute it, replace it with a placeholder, or cut it off, and repeated matches can lead to a strike. The camera mic would pick up the songs too, so camera audio doesn't avoid this. Streaming only the shows doesn't help either: the shows are where the commercial songs play.

The ID3 tags on the show MP3s (`Documents\xLights\Audio\Songs`) sort them like this:

| Risk | Songs | Why |
|---|---|---|
| Low | Auld Lang Syne | From archive.org (a public-domain folk-song collection) |
| Medium | O Come All Ye Faithful, The Virgin Mary Had a Baby Boy, Twelve Days of Christmas, We Wish You a Merry Christmas | The songs are traditional, but these are 2017 compilation recordings ("Christmas Carol"). Those are often registered with Content ID. |
| High | Rockin' Around the Christmas Tree, Dominick the Donkey, Feliz Navidad, Little Drummer Boy, What a Wonderful World, Happy New Year, Here Comes the Sun, Walking on Sunshine, Frosty the Snowman | Major-label recordings, and the songs themselves are under copyright |

**Live plan: always stream the video; stream the sound only when it is safe.**
- The relay mutes the live audio (an ffmpeg volume filter) whenever FPP is playing a track on a "muted" list. FPP's current sequence is available from its API or via Node-RED.
- The recording keeps the full audio for clips.
- Skits stay audible.
- During a muted song the trees perform in silence, and the stream title says "come and hear it on the street".
- Swap the medium-risk carols for public-domain or CC0 recordings (Musopen, archive.org, or a home recording) so they can be heard live too. They then need re-timing with `tools/lyric_timing.py` / `tools/xl_timing.py`.
- If even the muted stream gets flagged, fall back to video only.

**Playing on the street (separate from the stream).** In the UK, playing recorded music in public technically needs a PPL PRS licence (TheMusicLicence). That licence is aimed at businesses and organisations. A free display at a private home is a grey area, and enforcement against one is unheard of. Two things would change that:
- **Donations:** collecting donations, even for charity, makes it look like an event. Ask PPL PRS first.
- **YouTube rips:** several MP3s look like YouTube rips (Happy New Year, Here Comes the Sun, Walking on Sunshine). Buying them as downloads makes the sources clean.

**Open question:** a short email to PPL PRS describing the display would settle it. None of this is legal advice.

## Checks before buying

1. **Copyright test.** Rob requested live streaming on 24 Oct 2026; it can take up to 24 h to switch on. `tools/stream_test.py` runs the test from the PC; the steps are below. Note what gets flagged.
2. **The farmer.** Get permission, ideally in writing, and ask when they flail the hedge (cutting season is Sept–Feb). Check whether the hedge or verge is highway land.
3. **Privacy.** A camera that publishes the road falls outside the domestic CCTV exemption, so:
   - frame the house and trees
   - privacy-mask the road and pavement in the camera
   - keep camera audio off
   - stream only at show times
4. **WiFi at the hedge.** Stand at the hedge with a phone and check the signal from the router that will serve the camera. Until the Cudy is in place, use the Zyxel's 2.4 GHz.
5. **4G upload** at show times on a few evenings: at least 4 Mbps for 720p, or 6 Mbps for 1080p.

### Running the copyright test

`python -m tools.stream_test build` renders `previews/stream-test.mp4`: the trees singing Rockin' (high risk), O Come All Ye Faithful (medium) and Auld Lang Syne (low), back to back, about 9 minutes at 720p. Add song names (`data/songs/<name>.json`) to test others, or `--seconds 20` for a quick one.

1. **Set up the broadcast.** In YouTube Studio go to **Create → Go live → Stream**. Set visibility to **Unlisted**, made for kids **No**, and leave DVR on.
2. **Store the stream key.** Copy the key into a user environment variable called `YT_STREAM_KEY`. Set it the same way as `FPP_PASSWORD`, and never put it in git.
3. **Push the video.** Run `.venv\Scripts\python.exe -m tools.stream_test stream`. It sends the file in real time, so it takes as long as the video.
4. **Watch and record what happens.** Watch the Studio preview and the stream's **Copyright** notices during and after the run. For each song, note whether it played, was muted, was replaced, or the stream was stopped. Write the results here, and the auto-mute list comes from that.

## Phases

- **S0:** the checks above.
- **S1, bench:**
  - **ESPHome config:** deep-sleep schedule, MOSFET, battery sensor, fail-safes.
  - **Real draw:** measure it awake, asleep and with the camera on.
  - **Relay:** the relay on the Pi 5, with auto-mute and recording, for a 1-hour unlisted soak.
  - **Exposure:** set it against a lit tree.
- **S2, install** before 1 Dec: stake, box, aim and focus at dusk, privacy masks.
- **S3, clips tool:** cut recordings per sequence from FPP's log.
- **S4, Home Assistant** (in the HA repo, optional):
  - a camera entity and a hall board tile
  - a battery level and low-battery alert
  - skip/on-now overrides for the ESP32
