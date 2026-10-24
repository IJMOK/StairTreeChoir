# Show night

Draft, 23 Oct 2026. Everything here plays from the site's FPP player on a schedule; Home Assistant (M7) can later start it at sunset or hold it when nobody's home. Times are a proposal for Rob to change.

## Running order

UK sunset in December is about 15:50.

| Time | What plays | Sound |
|---|---|---|
| 16:00 | **Waiting** loop: slow rainbow across the choir, trees blinking, glancing about, one dozing off now and then | none, or quiet instrumental |
| every :15, :30, :45, 16:15 to 19:45 | **Announcement** (~13 s): "Next show at five o'clock!" (the 19:xx ones announce the last show, at eight) | the trees, lip-synced |
| 17:00, 18:00, 19:00, 20:00 (last) | **Show** (~15 min), then back to the waiting loop | full |
| after the 20:00 show | **Goodnight** skit, then lights off | |

Volume: a "quiet hours" level after 20:00 if the neighbours ask. FPP's scheduler runs this; the playlists are generated per site (M5) so every site gets the same shows.

## A show (~15 minutes)

Four songs plus short skits between them. Three set lists rotate through the evening so people who stay see something new.

| | Set A (17:00, 20:00) | Set B (18:00) | Set C (19:00) |
|---|---|---|---|
| Opening skit | Tuning up | Tuning up | Tuning up |
| 1 | Rockin' Around the Christmas Tree | Feliz Navidad | We Wish You a Merry Christmas |
| skit | Who's singing next? | Pip's joke | Bramble wakes up |
| 2 | Dominick the Donkey | Frosty the Snowman | Twelve Days of Christmas |
| skit | Bramble falls asleep | Who's singing next? | Pip's joke |
| 3 | Little Drummer Boy | O Come All Ye Faithful | The Virgin Mary Had a Baby Boy |
| 4 | We Wish You a Merry Christmas | Rockin' Around the Christmas Tree | Dominick the Donkey |
| Closing | Thank you / next show | Thank you / next show | Thank you / next show |

Between the pieces: 3–5 s of the waiting look so the songs don't run into each other.

## The choir

Six characters, one per sequence slot (left to right as you face them), so every site gets the same cast whichever physical trees it has. Names and voices are proposals.

| Slot | Name | Character | Voice (ElevenLabs, 24 Oct 2026) | Piper fallback |
|---|---|---|---|---|
| 1 | **Holly** | The conductor. Bossy, counts everyone in. | Alice (British, clear) | en_GB, female, crisp |
| 2 | **Ivy** | Holly's sidekick, agrees with everything. | Lily (British, warm) | en_GB, female, bright, pitched up |
| 3 | **Noel** | The show-off tenor. Holds every note too long. | Eric (smooth tenor) | en_GB, male, pitched down |
| 4 | **Jingle** | Over-excited. Talks fast. | Liam (energetic, fastest) | en_GB, male, pitched up |
| 5 | **Bramble** | Sleepy. Nods off between songs. | Bill (old, lowest, slowest) | en_GB, male, slow, low |
| 6 | **Pip** | The smallest voice. Tells terrible jokes. | Laura (quirky) | en_GB, female, high |

Voices: ElevenLabs premade voices with the eleven_v3 model, directed per line with audio tags (`[sleepily]`, `[giggles]`) in the scripts; tools/skit.py caches every clip, so re-runs are free. Picked by Claude from measured pitch and pace without listening, so they're proposals: auditions of three candidates per character are in the show folder's `Audio\Skits\auditions\`. To change one, set its voice id in data/voices.json and re-run the skits. Piper (`--engine piper`) stays as the free, offline fallback. Lip-sync uses the same lyric-timing tools as the songs, kept inside each line's known span of audio.

## Scripts (first drafts)

Eyes in brackets: the eye moves from tools/fx.py.

### Announcement (every quarter hour, one per show time)

> **Holly:** Hello everyone! We're the Stair Tree Choir!
> **Jingle:** And our next show starts at **five o'clock**!
> **Pip:** Bring your friends! And your grandma! And your grandma's friends!
> **Holly:** See you then! *(all: eyes roll)*

### Tuning up (opening)

> **Holly:** Places, everyone! Places!
> **Noel:** Mi-mi-mi-mi-miiiiiiiii… *(Noel's eyes: rainbow)*
> **Holly:** Thank you, Noel.
> **Noel:** …miiiiiiiiiiiii—
> **Holly:** THANK you, Noel. *(everyone looks at Noel)*
> **Holly:** Bramble? … Bramble!
> **Bramble:** *(eyes open)* I'm awake! I'm awake!
> **Holly:** One, two, three, four!

### Who's singing next?

> **Jingle:** Ooh, ooh, can I sing the next one? Can I? Can I?
> **Holly:** Everyone sings the next one, Jingle.
> **Jingle:** Even me?!
> **Ivy:** Especially you.

### Pip's joke

> **Pip:** What do you call a tree that's afraid of Christmas?
> **Ivy:** I don't know, Pip, what?
> **Pip:** A *fir*-aid-y cat!
> *(everyone looks at Pip; long pause; Noel's eyes roll)*
> **Holly:** …Next song.

### Bramble falls asleep / wakes up

> **Bramble:** *(yawns)* Is it nearly the end?
> **Holly:** It's the second song, Bramble.
> **Bramble:** zzzz… *(Bramble's eyes close; snoring)*
> *(later)* **Holly:** BRAMBLE! **Bramble:** Present!

### Thank you / next show

> **Holly:** Thank you for listening! We've been the Stair Tree Choir!
> **Pip:** Our next show is at **six o'clock**!
> **Everyone:** Merry Christmas!

### Goodnight (21:00)

> **Holly:** That's all for tonight, everyone.
> **Bramble:** Finally… *(eyes close)*
> **Pip:** Goodnight! Sleep tight! Don't let the reindeer bite!
> **Everyone:** Goodniiiight! *(outlines fade out one by one)*

## Status (24 Oct 2026)

Built: skits with ElevenLabs voices (tools/skit.py), skit arrangements, the waiting loop and the goodnight fade, FPP playlists and schedule per site (tools/gen_site_config.py), and one ready-to-copy bundle per player with the night's real running times (tools/fpp_bundle.py → [show-plan.md](show-plan.md)).

Still to do: the first run on a real FPP player (fpp/README.md "Not verified"), then HA (M7).
