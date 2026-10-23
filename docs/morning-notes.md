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
