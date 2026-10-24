# Notes for Rob (23 Oct 2026, late)

The usage limit stopped the overnight run here. State:

**Done tonight:** all 7 new songs have lyric timing (Audio/*.json) and beats (Audio/*.beats.json).
- Little Drummer Boy: LRCLIB timing was from another recording (+5.5s); now shifted, 14 lines fell back to it.
- Feliz Navidad: 9 lines fell back to LRCLIB timing (lines 23, 33-40).
- Frosty, We Wish You, O Come All Ye Faithful, Virgin Mary, Twelve Days: lyrics are Whisper transcriptions of your recordings. **Please skim the .lyrics.txt files in Documents\xLights\Audio for mishearings**, then rerun lyric_timing for any you fix.

**Not done (next session):**
1. Sequences for the 7 songs and 12 skits. Plan: generate the .xsq files directly (clone Rockin's structure, own timing track with word/phoneme breakdown verified against xLights' breakdown of Rockin's Choir_1) so nobody has to click Sequence Settings. Fallback: you do File → New per song.
2. Arrangements (data/songs/*.json) for the 7 songs; Twelve Days with one tree per day.
3. Skits: run tools/skit.py on data/skits/*.json (audio already works; listen to Audio/Skits/tuning-up.wav and pips-joke.wav).
4. Waiting-loop and goodnight sequences; FPP playlists and schedule per site (M5).
5. Build guide and test checklist (M6).

## Songs agent (24 Oct 2026)

**Done, all in xLights (show folder) and committed (data/songs/*.json):** every lyric line checked from the render with `check_render`.

| Sequence | Lines | check_render |
|---|---|---|
| Feliz Navidad | 40 | 40/40 |
| Little Drummer Boy | 57 | 57/57 |
| We Wish You a Merry Christmas | 32 | 32/32 |
| O Come All Ye Faithful | 24 | 24/24 |
| The Virgin Mary Had a Baby Boy | 48 | 48/48 |
| Twelve Days of Christmas | 102 | 102/102 |
| Frosty the Snowman | 28 | 28/28 |
| 11 skits (Skit announce-17 ... Skit whos-next) | 3-8 each | all match |
| Waiting (300 s loop, no audio) | 0 | n/a |
| Goodnight (closer, ends on black) | 4 | 4/4 |

Frosty the Snowman is now sequenced (28/28 lines, Set B's second song).

**How sequences are made now (no clicks):** `GET /newSequence?mediaFile=<path>&frameMS=50&view=All%20Models&force=true` creates it without the Sequence Settings dialog (`durationSecs=300` instead of mediaFile for an animation). Then saveSequence, closeSequence, `tools.xsq` (it says "nothing to add": new sequences already list the Outlines group from the layout), `tools.xl_timing add`, openSequence.

**Please check / decide:**
1. **Feliz Navidad, lines 33-40** are crammed into the last 4.5 s (LRCLIB's own timing; the recording fades from 129 s and is below -20 dB after ~134 s). The whole choir mouths them together in the fade. If you'd rather, delete those lines from the lyrics file and re-time.
2. **Carol re-timing** used Whisper medium.en on your corrected lyrics. Three hand fixes in the show folder's timing JSONs (re-running lyric_timing would undo them): Virgin Mary lines 24 and 36, the last word(s) had been placed after the instrumental and were moved back to follow the line (word lengths copied from line 12, the same phrase); Twelve Days line 1, the first word was squashed to zero length and was set to 9.61-10.44 s from a cold transcription. Two isolated words are still near zero length (O Come line 12 word 4, Feliz line 32 word 1): one missing mouth shape each.
3. **O Come line 11** runs 12.3 s in both Whisper models. It's a slow recording so it's probably right, but worth a look.
4. **Whisper medium.en download** failed its checksum twice through Whisper (truncated); I fetched it with curl, verified the SHA256 and put it in `~/.cache/whisper`.
5. **xLights wasn't running** at the start; I started it and closed the "Tip of the day" and "Update Available" dialogs (WM_CLOSE). An xLights update is available.
6. **Dictionary** (`Documents\xLights\user_dictionary`, not in git): added Navidad, the Spanish word for "year" (key with only ASCII uppercased, UTF-8), PUM, the four hyphenated Twelve Days gift words (ALAYING etc.), and the skit words (FIRRAIDY, the two long "mi" spellings, the long goodnight, the snore). Nothing is missing in any timing file now. **Restart xLights** before importing any new timing in the GUI, so it reloads them.
7. **Code changes:** `tools/xl_timing.py` and `tools/lyric_timing.py` read the dictionaries as UTF-8 and uppercase ASCII only, as xLights does (before, a key with ñ could never match; Rockin' and Dominick still verify exactly). `tools/arrange_song.py`: arrangements may have no lines (Waiting), and new keys `end_at`/`end_fade` clip everything (Faces too) at a time and fade out the last effects. Goodnight uses `end_at` 9.9 s + 1.2 s fade: the fseq's last 21 frames are all zero, so FPP holding the last frame leaves the trees dark. Tests added.
8. **Looks I swapped after checking contact sheets:** twinkle, snow, shimmer and sparse chases read dark on a single outline (especially with resting trees dimmed), so I replaced them with butterflies, beat pulses, marquees, plasma or a steady glow. `pulse` stills look dim because they catch the beat decay; in motion they flash on every beat.
9. **Skit bramble-sleeps** is almost dark (outlines off, a few snowflakes). That's the skits agent's design, and fine for a sleeping tree, but have a look.
10. **Little Drummer Boy:** the drum-sound lines get their own short generated sections (colour hit on every beat), so the file has 49 sections. To change a look for a whole verse, edit all of that verse's sections (names `verseN` and `verseN-drum`).

## Folder tidy (24 Oct)

The show folder (`Documents\xLights`) is reorganised: each song's audio, lyrics, beats and timing are in `Audio\Songs\` named after its sequence (e.g. `Feliz Navidad.mp3`, `Feliz Navidad.timing.json`); skit timing is `Audio\Skits\<name>.timing.json`; Frosty is in `Audio\Parked\`; old test files and `.xsq.bak` copies are in `_Archive\`. Sequences stay in the top level with the same names. Every sequence's media path and `data/songs/*.json` were updated, all 21 re-rendered and re-checked (every line matches), and the FPP playlists now name the media e.g. `Feliz Navidad.mp3`, so upload the audio under those names. Backup of the folder as it was (without Voices and RenderCache): `Documents\xLights-backup-2026-10-24`. Old to new names: [show-folder-moves.md](show-folder-moves.md). Map: [folders.md](folders.md).

## Frosty the Snowman (24 Oct 2026)

Frosty is no longer parked: files are in `Audio\Songs\`, sequence `Frosty the Snowman.xsq` (timing track `Frosty`), arrangement `data/songs/frosty-the-snowman.json`, 28/28 lines. Set B's second song is now Frosty (FPP playlists regenerated).

**Please skim `Audio\Songs\Frosty the Snowman.lyrics.txt` for Whisper mishearings.** Line 18 needs a look: forced alignment had stretched it across 25 s (one word at 82 s, the rest at 101-107 s), while a cold Whisper pass heard singing at 78-90 s and 101-108 s. I spread its 14 words over those two sung stretches by hand in the timing JSON; re-running lyric_timing would undo that, so fix the lyrics file first if line 18 is wrong, then redo the hand fix. Three words around 146.7 s have zero length in the timing; xLights copes with it.
