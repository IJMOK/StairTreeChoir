# Show night

Draft, 23 Oct 2026. Everything here plays from the site's FPP player on a schedule; Home Assistant (M7) can later start it at sunset or hold it when nobody's home. Times are a proposal for Rob to change.

## Running order

UK sunset in December is about 15:50.

| Time | What plays | Sound |
|---|---|---|
| 16:00 | **Waiting** loop (10 minutes, ten one-minute scenes): the choir mucking about between shows, a different background in every scene. Mexican waves, Noel showing off, a game of catch, Bramble nodding off, Ivy copying Holly, Jingle fidgeting, watching passers-by ([below](#the-silent-loops)) | none |
| every :15, :30, :45, 16:15 to 19:45 | **Announcement** (~13 s): "Next show at five o'clock!" (the 19:xx ones announce the last show, at eight) | the trees, lip-synced |
| 17:00, 18:00, 19:00, 20:00 (last) | **Show** (~15 min), then back to the waiting loop | full |
| 21:00 | **Goodnight** skit; the trees settle into a dim, sleepy breath | the trees |
| after the Goodnight | **Night** loop: the trees doze, yawn, peek and giggle, dim and slow, until lights out | none |
| lights out | Home Assistant stops the Night loop gracefully when the living room lights go off: the scene playing finishes, then **Lights Out** (20 s: last yawns, Holly shushes, eyes close, the trees go dark one by one). FPP's backstop: the Night loop's window closes at **23:30** with the same graceful stop. | none |

Specials (Saturday Special at 18:00 on December Saturdays, New Year's Eve to the midnight countdown, New Year's Day 15:00–19:00): [specials.md](specials.md).

Volume: a "quiet hours" level after 20:00 if the neighbours ask. FPP's scheduler runs this; the playlists are generated per site (M5) so every site gets the same shows.

## A show (~15 minutes)

Four songs plus short skits between them. Three set lists rotate through the evening so people who stay see something new.

| | Set A (17:00, 20:00) | Set B (18:00) | Set C (19:00) |
|---|---|---|---|
| Opening skit | Tuning up | Tuning up | Tuning up |
| 1 | Rockin' Around the Christmas Tree | Feliz Navidad | We Wish You a Merry Christmas |
| skit | Who's singing next? | Pip's joke | Bramble falls asleep |
| 2 | Dominick the Donkey | Frosty the Snowman | Twelve Days of Christmas *(Bramble asleep)* |
| skit | Bramble falls asleep | Who's singing next? | Bramble wakes up |
| 3 | Little Drummer Boy *(Bramble asleep)* | O Come All Ye Faithful | The Virgin Mary Had a Baby Boy |
| skit | Bramble wakes up | | |
| 4 | We Wish You a Merry Christmas | Rockin' Around the Christmas Tree | Dominick the Donkey |
| Closing | Thank you / next show | Thank you / next show | Thank you / next show |

Bramble's story (24 Oct 2026) is complete in Sets A and C: he nods off, sleeps through the next song (eyes shut, outline a slow dim blue breath, the others cover his lines; Twelve Days' fifth day goes to Jingle and Pip either side of him), and Holly wakes him after it. Little Drummer Boy and Twelve Days have him asleep throughout, so they may only follow "Bramble falls asleep" (a test checks the set lists).

Between the pieces: 3–5 s of the waiting look so the songs don't run into each other.

## The choir

Six characters, one per sequence slot (left to right as you face them), so every site gets the same cast whichever physical trees it has. Names and voices are proposals. Their backstories, name-tag lines and answers for curious visitors: [backstory.md](backstory.md).

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
> **Everyone:** Goodniiiight! *(they settle one by one, Noel last after his long note: heavy eyes, a dim warm breath; Bramble's already asleep. That's where the Night loop picks up.)*

## The silent loops

Built 25 Oct 2026 (tools/loops.py, arrangements in data/loops/). No audio. Each loop is a run of short sequences, one scene each, played in order by its FPP playlist and repeated; short so that a graceful stop (lights out) only waits for the end of the scene that's playing. Each playlist has a **lead-out** that FPP plays after a graceful stop and then goes idle; a hard stop (a show cutting in) skips it. The characters act through eyes (look at each other, roll, wink, heavy lids, close), outline looks of their own (glow, breathe, bounce, swell, sparkle, a ball of light running round) and mouth shapes (yawn, silent hum, giggle, chatter, whisper, snore, shush); otherwise mouths rest on the lip. Nothing strobes; the quickest thing is Jingle's bounce on his own tree. Character colours: Holly red, Ivy green, Noel gold, Jingle orange, Bramble blue, Pip pink.

| Playlist | Pieces | Lead-out | When |
|---|---|---|---|
| `Waiting` | Waiting 1-10, 60 s each (10 min) | Lights Out | 16:00 to the Goodnight, scheduled; shows cut in with a hard stop |
| `Waiting Asleep` | Waiting Asleep 1-10: the same scenes with Bramble asleep throughout (the others still nudge him; he sleeps on) | Lights Out | New Year's Eve, from Bramble nodding off (23:20) to the countdown |
| `Night` | Night 1-8, 50 s each (6:40), brightness 45 % | Lights Out (20 s, ends black) | after the 21:00 Goodnight until lights out, backstop 23:30; also 00:00-00:30 on New Year's Day, after the countdown |
| `Night Christmas Eve` | Night Christmas Eve 1-3, 40 s each: all asleep for Santa, only the gentlest stirring | Lights Out Asleep (12 s, the sleepers fade out one by one) | Christmas Eve after the Goodnight, backstop 23:30 |
| `Morning` | Morning 1-6, 45 s each, brightness 85 % | Morning Lights Off (15 s: a goodbye wave, a wink each, off one by one) | not scheduled: Home Assistant starts it with Rob's alarm and stops it at the morning lights out (sunrise + 90 min). Backstop: repeat off and the six pieces listed 40 times (3 hours), so it ends by itself through its lead-out |

Every scene, with its background look:

| Piece | Length | Background | What happens |
|---|---|---|---|
| Waiting 1 | 60 s | rainbow wash | Mexican wave: down the line, back in everyone's own colour, then faster; Bramble is late |
| Waiting 2 | 60 s | choir butterfly | Noel shows off with a rainbow shimmer; the others roll their eyes; Holly stops him; he tries again |
| Waiting 3 | 60 s | breathing rainbow | Pass the ball: Pip and Jingle throw a ball of light over Bramble, up to Holly, who throws it back; Pip drops it |
| Waiting 4 | 60 s | spirals | Bramble nods off; Ivy tells Holly; Holly's nudge runs down the line and he wakes with a start |
| Waiting 5 | 60 s | marquee | Ivy copies everything Holly does, a beat behind; Holly notices; Pip joins in |
| Waiting 6 | 60 s | plasma | Jingle can't keep still: bouncing, eyes rolling, chattering; Holly shushes him; Pip joins in |
| Waiting 7 | 60 s | rainbow sweep, then breathing | Passers-by: the trees watch someone walk past, show off to them, pose; a silent hum to finish |
| Waiting 8 | 60 s | breathing rainbow | The silent hum: Holly conducts, Noel holds the last note far too long, Holly stops him, he bows |
| Waiting 9 | 60 s | a colour each, then icy spirals | Colour relay: every tree passes its colour to its neighbour; Pip muddles it; then the ball goes round everyone |
| Waiting 10 | 60 s | icy spirals, then fire | Snow: everyone looks up in wonder; Jingle's delighted; Pip catches a snowflake; then cosy by the fire |
| Night 1 | 50 s | warm breath | Settling down: yawns go round, Bramble's already snoring, Jingle's wide awake until Holly shushes him |
| Night 2 | 50 s | blue breath | Can't sleep: Jingle peeks, whispers to Pip, Pip whispers back; Holly shushes; Jingle peeks again |
| Night 3 | 50 s | low fire | Doze and poke: Noel nods off, Jingle pokes him and pretends to be asleep; later Pip does it too |
| Night 4 | 50 s | purple breath | Snore glow: Bramble snores, his glow swelling with every snore; Ivy rolls her eyes; Holly's nudge travels down the line |
| Night 5 | 50 s | teal breath | Giggles: Pip and Jingle set each other off, a sparkle passing between them over sleeping Bramble; Holly shushes |
| Night 6 | 50 s | navy breath | Peekaboo: they take turns to peek; Pip and Holly peek at each other at the same moment; Bramble talks in his sleep |
| Night 7 | 50 s | slow icy spiral | Noel's dream: asleep, he glitters gold and silently sings his solo; Holly rolls her eyes |
| Night 8 | 50 s | slow blue breath down the line | Deep sleep: slow breaths roll down the line, soft snores; Holly checks everyone's asleep |
| Night Christmas Eve 1-3 | 40 s | everyone's sleeping breath | Pip peeks to see if Santa's been; Jingle giggles in a dream; Ivy hums in her sleep; Noel dreams in gold; Holly checks; Jingle looks up for the sleigh; Bramble snores |
| Morning 1 | 45 s | pink breath | Waking up: Jingle's been awake for ages; eyes open one by one with yawns and stretches; Bramble snores on |
| Morning 2 | 45 s | gold breath | Holly's roll call: she looks at each tree in turn and they answer with a blink and a colour pop; Jingle answers too early, Noel shows off, Bramble doesn't answer at all |
| Morning 3 | 45 s | sunrise spirals | Bramble won't wake: Holly and Ivy nudge him, then Pip and Jingle from the other side; he opens one eye, and shuts it again |
| Morning 4 | 45 s | rainbow wash | Pip's sunrise: a sparkle on Pip spreads up the line in gold and everyone looks up; then Noel warms up, silently |
| Morning 5 | 45 s | daylight marquee | Off to work and school: the trees watch people go past, Jingle bounces at them, everyone stretches up in daylight |
| Morning 6 | 45 s | breathing rainbow | Ready for the day: everyone hums; Bramble finally wakes properly and the others cheer with a gold wave |

**Lights out** comes from Home Assistant (Rob's HA repo): in the evening when the living room lights go off, in the morning at sunrise + 90 min; it stops the playlist gracefully (`ALLPLAYLISTS` or the playlist by name). FPP doesn't restart a playlist stopped by hand in the same schedule window (Scheduler.cpp, "just force stopped"), so the trees stay dark. If HA never says, the Night loop's schedule window ends at 23:30 (00:30 on New Year's night) with a graceful stop: dark by about 23:31:30 at the latest.

The Goodnight (21:00) now ends on the Night loop's first state (heavy eyes, dim warm breath, Bramble asleep) instead of black, and the Christmas Eve goodnight ends with everyone asleep instead of fading out, so each hands straight over to its night loop. The New Year's Day "Goodnight Season" still ends dark: no night loop after the season's last goodnight.

## Status (24 Oct 2026)

Built: skits with ElevenLabs voices (tools/skit.py), skit arrangements, the silent loops (Waiting, Night, Morning, 25 Oct 2026), FPP playlists and schedule per site (tools/gen_site_config.py), and one ready-to-copy bundle per player with the night's real running times (tools/fpp_bundle.py → [show-plan.md](show-plan.md)).

Still to do: the first run on a real FPP player (fpp/README.md "Not verified"), then HA (M7).
