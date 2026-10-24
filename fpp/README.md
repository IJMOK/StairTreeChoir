Per-site FPP player config (DDP outputs per tree) and provisioning notes (milestone M5).

# What is generated here

`python -m tools.gen_site_config` (part of `python -m tools.build`) writes, for each site in `data/sites.json`:

| File | What it is | Goes to |
|---|---|---|
| `<site>/co-universes.json` | FPP channel outputs: one **DDP - One Based** output per tree (tree IP, start channel `(slot-1)*276+1`, 276 channels) | `POST /api/channel/output/universeOutputs` |
| `<site>/playlists/*.json` | Waiting, Announce 17/18/19/20/last, Show A/B/C, Goodnight | `POST /api/playlist/<name>` |
| `<site>/schedule.json` | The nightly schedule from `docs/show-night.md` | `POST /api/schedule`, then `POST /api/schedule/reload` |

Do not edit these by hand. Change `tools/gen_site_config.py` (set lists, times, season, media extensions) or `data/sites.json` and rebuild. The source reference for every field is in the generator's docstring (checked against FPP 10.3, tag 10.3, 21 Oct 2026).

Why DDP "One Based" (type 5) and not "Raw" (type 4): in `src/channeloutput/DDP.cpp` the DDP offset in the packets is `startChannel-1` for Raw and always 0 for One Based. WLED's first LED is DDP offset 0, so every tree needs One Based; FPP still reads the tree's data from the sequence at its start channel.

## The show schedule

Every site plays the same thing (only its trees differ). Times are the proposal in `docs/show-night.md`; the generator holds them as constants.

| Time | Playlist | Notes |
|---|---|---|
| 16:00 to 21:00 | `Waiting` | loops, no audio, hard stop so a show can cut in at once |
| 16:15 16:30 16:45 | `Announce 17` | "next show at five" |
| 17:15 17:30 17:45 | `Announce 18` | |
| 18:15 18:30 18:45 | `Announce 19` | |
| 19:15 19:30 19:45 | `Announce last` | "last show of the night at eight" (the 20:00 show); no announcements after it |
| 17:00 and 20:00 | `Show A` | |
| 18:00 | `Show B` | Frosty is parked: its slot is Little Drummer Boy |
| 19:00 | `Show C` | |
| 21:00 | `Goodnight`, then nothing | the waiting window ends at 21:00; the date range is 1 to 31 Dec 2026 |

How FPP resolves this (read from `src/Scheduler.cpp`): an entry's priority is its position in `schedule.json` (earlier wins). Goodnight is first, then the shows, then the announcements, then `Waiting`. A higher-priority entry starting stops whatever is running, using the running entry's stop type, and the interrupted entry is restarted afterwards if its window is still open; a lower-priority entry waits for a running one and starts when the player is idle if its window is still open. So after a show or announcement the waiting loop comes back by itself, and a show that runs past :15 just delays that quarter-hour announcement. Show windows are 30 minutes (so a 15 minute show is never cut off), announcement windows 10 minutes. Entries of the same kind never overlap; the tests check the priority order.

## Provisioning a site player

1. **Flash** the SD card with FPP 10.x (the 64-bit Raspberry Pi image from https://github.com/FalconChristmas/fpp/releases; the generator was checked against 10.3). Boot the Pi on the site router (Ethernet or the site Wi-Fi). Give it a fixed IP outside the trees' range (trees are 192.168.8.101 to .114; for example .20) and a hostname such as `stairtree-fpp-site-a` under Settings > Network. FPP mode stays Player.
2. **Check the clock and timezone** (Settings > Time): the schedule is local time. A Pi has no real-time clock, so it needs internet or an NTP server on the router once per boot. Look at the time on the Status page before trusting the schedule.
3. **Audio**: plug in the USB sound card, then Settings > Av > Audio Output Device and pick it (API: `PUT /api/settings/AudioOutput` with a card name from `GET /api/settings/AudioOutput/options`; it needs a reboot). Keep the Pi volume moderate and set the real level on the amp.
4. **Upload the generated files** from the repo root (`<pi>` is the Pi's address, `<site>` e.g. `site-a`). FPP's API wants `Content-Type: application/json`:

   ```
   curl -X POST -H "Content-Type: application/json" --data-binary @fpp/<site>/co-universes.json http://<pi>/api/channel/output/universeOutputs
   for f in fpp/<site>/playlists/*.json; do n=$(basename "$f" .json); curl -X POST -H "Content-Type: application/json" --data-binary @"$f" "http://<pi>/api/playlist/${n// /%20}"; done
   curl -X POST -H "Content-Type: application/json" --data-binary @fpp/<site>/schedule.json http://<pi>/api/schedule
   curl -X POST http://<pi>/api/schedule/reload
   curl -X POST http://<pi>/api/system/fppd/restart
   ```
   The loop is bash (Git Bash). Without it: copy the files into `/home/fpp/media/config/` (`co-universes.json`, `schedule.json`) and `/home/fpp/media/playlists/` over Samba or SFTP and restart FPPD, or re-enter them in the UI (Input/Output Setup > Channel Outputs > E1.31/ArtNet/DDP; Content Setup > Playlists; Scheduler).
5. **Upload the sequences and audio** from xLights' render output: every `<Sequence name>.fseq` into Sequences and its audio into Music, with File Manager in the FPP UI or `curl -X POST --data-binary @"X.fseq" "http://<pi>/api/file/Sequences/X.fseq"` and `.../api/file/Music/X.mp3`. The names must match the playlists exactly:
   - songs: Rockin Around the Christmas Tree, Dominick the Donkey, Feliz Navidad, Little Drummer Boy, We Wish You a Merry Christmas, O Come All Ye Faithful, The Virgin Mary Had a Baby Boy, Twelve Days of Christmas (audio `<name>.mp3`, from the show folder's `Audio\Songs\`)
   - skits: `Skit <name>` for each `data/skits/<name>.json`, e.g. `Skit tuning-up`, `Skit announce-17` (audio `<name>.wav` from `Audio\Skits\`, e.g. `tuning-up.wav`)
   - `Waiting` (no audio) and `Goodnight` (audio `goodnight.wav`, the goodnight skit's)
6. **Validate**: `GET /api/playlists/validate` (or the warnings on the Playlists page) must list no problems, which means every sequence and media file exists.
7. **Test, in this order**:
   1. Trees powered and on the site router: each tree's WLED page (http://192.168.8.1NN) loads.
   2. Status page: the channel output rows show no warnings. Content Setup > Test Mode (all channels, RGB chase) lights every tree in slot order.
   3. Start `Show A` by hand from the Playlists page: audio from the speaker, mouths in step with the voices on all the site's trees. A tree that stays dark: check its IP, and that its WLED Info shows realtime.
   4. Start `Announce 17`, then `Goodnight`: after Goodnight the lights go out and stay out.
   5. Move the Pi clock (or edit the entry times for a few minutes) to watch `Waiting`, an announcement and a show hand over to each other.

## Not verified (no hardware yet), for the bench

- The generated schedule has never run on a device. On the Scheduler page check that the order is the priority described above, that `Waiting` resumes after an announcement or a show, and that a show started by hand is not cut off.
- Whether the trees go dark after `Goodnight`. The `Goodnight` sequence should end on black. FPP's "Blank between sequences" setting is left off.
- Media file types: songs `.mp3` and skits `.wav` are assumptions from the audio tools; change `SONG_MEDIA_EXT` / `SKIT_MEDIA_EXT` in the generator if the files differ. The media names come from each arrangement's `audio` (`data/songs/*.json`); the extensions are only the fallback.
- Pacing (90 Mbps) and "multi-threaded blocking" are the FPP UI defaults; frame timing over the site Wi-Fi is the M0 test.
- The playlist `playlistInfo` durations are 0; FPP fills them in when a playlist is saved from its own UI. They only affect the duration shown.
- The `curl` commands are built from the API source and were not run against a live FPP. The UI route always works.
