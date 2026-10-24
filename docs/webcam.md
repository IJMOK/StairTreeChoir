# Show webcam

A camera in the farmer's hedge across the road streams the Site A show live to the village, family and friends. It is separate from the tree build and is not needed for 1 Dec. This page is the scope and BOM; nothing is built yet (24 Oct 2026).

## Constraints

- The hedge is about **20 m** from the house with a clear view. It has **no power and no WiFi**, and it is the farmer's land.
- The internet is the Huawei B818 4G hub, with unlimited data.
- The show runs 16:00–21:00 every evening in December, plus the specials in [specials.md](specials.md): Saturday 18:00, NYE to midnight, NYD 15:00–19:00.
- Keep it cheap: about £150–200. An earlier draft with a point-to-point link and a 100 Ah battery came to £560+ and was turned down.

## Design

```
[hedge]  WiFi outdoor camera (12V) <- 12V timer <- 3A fuse <- 12V 20Ah LiFePO4   (one box at the foot of a stake)
             ~~~ 2.4 GHz WiFi, ~20 m open air ~~~
[garden] Site A Cudy WR3000 (outdoors at the site box) -> home LAN
         Site A Pi 5 (FPP): ffmpeg takes the camera's RTSP feed (video copied) + FPP's own audio -> YouTube Live
```

**Network.** No bridge. The Site A router is already outdoors in the front garden, so the camera joins its WiFi across about 20 m of open air. If the signal at the hedge is weak, a directional antenna on the Cudy (about £10) fixes it.

**Camera.** A cheap outdoor WiFi camera, for example a Tapo C320WS/C325WB (ColorPro, good in the dark) or a Reolink RLC-510WA. Before ordering, check that it:
- has RTSP output
- runs on 12V DC
- can switch IR off, so the hedge leaves don't flare
- lets you turn the exposure down if possible, so the pixels don't blow out

At 20 m a fixed lens of about 4–6 mm frames the house front, so no zoom is needed. The camera mic stays off: the stream gets clean sound from FPP instead, and passers-by aren't recorded.

**Power.**

| | |
|---|---|
| Camera, IR off | ~4 W |
| On for 15:45–21:15 (5.5 h) | ~22 Wh a night |
| 12V 20 Ah LiFePO4 | 256 Wh, ~200 Wh usable |
| **Runtime** | **~8 nights per charge**; carry it home and charge it indoors |

NYE (to midnight) uses about 12 Wh extra. A 12V programmable timer relay switches the camera on only for the show window and draws almost nothing when off. No solar: December yield is poor, LiFePO4 must not charge below 0°C, and a panel on the hedge invites theft.

**Stream.**
- ffmpeg runs on the Site A Pi 5 at low priority (`nice`). It copies the video, so the Pi never transcodes.
- Audio comes from FPP's own output through an ALSA loopback and is encoded to AAC. A one-off `-itsoffset` cancels the camera's ~1–2 s delay.
- If the relay ever disturbs FPP timing, move it to a separate Pi with one of the spare USB sound cards on a split of the amp input.
- The stream goes to YouTube Live: an unlisted link for family, posted in the village Facebook group. About 720p–1080p at 2.5–4 Mbps, roughly 1–2 GB an hour.

### Version 2 (next season)

An ESPHome ESP32 with a MOSFET and a voltage divider (about £10, powered by a spare Mini560):
- gives HA control and follows the FPP schedule
- reports battery voltage
- keeps the timer as a fallback

It stays on WiFi all day for about 10 Wh/day, which cuts runtime to about 5 nights per charge. Moving up to a 30 Ah battery covers that.

## BOM

UK prices are rough; check them when ordering.

| Qty | Item | Notes | Est. £ |
|---|---|---|---|
| 1 | Outdoor WiFi camera: RTSP, 12V input, colour night vision | e.g. Tapo C320WS/C325WB or Reolink RLC-510WA | 35–65 |
| 1 | 12V 20 Ah LiFePO4 battery | | 55–75 |
| 1 | 14.6V LiFePO4 charger | Mains, used at home | 20 |
| 1 | 12V digital timer relay | Switches the camera on for the show window | 8 |
| 1 | Inline fuse holder | 3A blade fuse from stock | 3 |
| 1 | Box for the battery and timer: an ammo box, or printed from `enclosure/sealed-box.scad` | Spare PG7 gland for the camera lead | 0–10 |
| 1 | Stake or post, or a clamp on an existing hedge stake, plus band clamps | Camera at about 2 m | 10–15 |
| 1 | Cable lock + camo tape | | 10 |
| – | Site A Pi 5 (FPP), Cudy site router | Already owned or planned | 0 |
| | **Total** | | **≈ £140–205** |
| opt | Directional 2.4 GHz antenna for the Cudy | Only if the signal at the hedge is weak | 10 |
| v2 | ESP32 + logic-level MOSFET module + divider resistors | Mini560 from the tree spares | 10 |
| v2 opt | 30 Ah LiFePO4 instead of 20 Ah | Covers the ESP32's standby draw | +25 |

## Music copyright

This is the biggest risk to the stream. YouTube Content ID (and Facebook's Rights Manager) matches **recordings**. A carol that is out of copyright still gets flagged if the recording is a modern one. A match on a live stream can mute it, replace it with a placeholder, or cut it off, and repeated matches can bring a strike. The camera mic would pick up the songs too, so using camera audio doesn't avoid this.

The ID3 tags on the show MP3s (`Documents\xLights\Audio\Songs`) sort them like this:

| Risk | Songs | Why |
|---|---|---|
| Low | Auld Lang Syne | From archive.org (a public-domain folk-song collection) |
| Medium | O Come All Ye Faithful, The Virgin Mary Had a Baby Boy, Twelve Days of Christmas, We Wish You a Merry Christmas | The songs are traditional, but these are 2017 compilation recordings ("Christmas Carol"), which are often registered with Content ID |
| High | Rockin' Around the Christmas Tree, Dominick the Donkey, Feliz Navidad, Little Drummer Boy, What a Wonderful World, Happy New Year, Here Comes the Sun, Walking on Sunshine, Frosty the Snowman | Major-label recordings, and the songs themselves are under copyright |

**Plan: always stream the video; stream the sound only when it is safe.**
- The relay mutes its audio (an ffmpeg volume filter) whenever FPP is playing a track on a "muted" list. FPP's current sequence is available from its API or via Node-RED.
- Skits (our own ElevenLabs voices), the Waiting loop, announcements and Goodnight stay audible.
- During a muted song the trees perform in silence, and the stream title says "come and hear it on the street".
- Swap the medium-risk carols for public-domain or CC0 recordings (Musopen, archive.org, or a home recording) so they can be heard too. They then need re-timing with `tools/lyric_timing.py` / `tools/xl_timing.py`.
- If even the muted stream gets flagged, fall back to video only.
- Self-hosting (Owncast on a VPS) avoids Content ID but still needs a music licence for a public audience. That isn't worth it here.

**Playing on the street (separate from the stream).** In the UK, playing recorded music in public technically needs a PPL PRS licence (TheMusicLicence). That licence is aimed at businesses and organisations. A free display at a private home is a grey area, and enforcement against one is unheard of. Two things change that:
- **Donations.** Collecting donations, even for charity, makes it look like an event; ask PPL PRS first.
- **Sources.** Several MP3s look like YouTube rips (Happy New Year, Here Comes the Sun, Walking on Sunshine). Buying them as downloads makes the sources clean.

**Open question:** a short email to PPL PRS describing the display would settle the licence question. None of this is legal advice.

## Checks before buying

1. **Copyright test.** Enable live streaming on the YouTube channel; this takes 24 h. Then run a 20-minute unlisted test from the PC with one high-risk song, one carol and Auld Lang Syne, and note what gets flagged.
2. **The farmer.** Get permission, ideally in writing, and ask when they flail the hedge (cutting season is Sept–Feb). Check whether the hedge or verge is highway land.
3. **Privacy.** A camera that publishes the road falls outside the domestic CCTV exemption, so:
   - frame the house and trees
   - privacy-mask the road and pavement in the camera
   - keep the camera audio off
   - stream only at show times
4. **WiFi at the hedge.** Stand at the hedge with a phone and check the signal from the router that will serve the camera. Until the Cudy is in place, use the Zyxel's 2.4 GHz.
5. **4G upload** at 16:00–21:00 on a few evenings: at least 4 Mbps for 720p, or 6 Mbps for 1080p.

## Phases

- **S0:** the checks above.
- **S1, bench:**
  - Camera, battery and timer on the table; measure the real draw.
  - A 1-hour unlisted stream from the Pi 5 with FPP audio and the auto-mute working.
  - Set the exposure against a lit tree.
- **S2, install** before 1 Dec: stake, box, then aim and focus at dusk, then privacy masks.
- **S3, Home Assistant** (in the HA repo, optional and later):
  - a camera entity and a hall board tile
  - Node-RED starts and stops the stream with the FPP schedule
  - the v2 ESP32 adds battery level and power control
