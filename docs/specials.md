# Specials: Saturday Special, New Year's Eve, New Year's Day

Plan, 24 Oct 2026, from Rob's answers. Nothing here is built yet; the build order is at the end. The normal night is in [show-night.md](show-night.md).

## The season with specials

| Dates (2026–27) | Night |
|---|---|
| 1–30 Dec, Sun–Fri | Normal night (show-night.md) |
| Sat 5, 12, 19, 26 Dec | Normal night, but **18:00 is the Saturday Special** |
| Thu 31 Dec | **New Year's Eve**: normal shows, then late shows and the midnight countdown |
| Fri 1 Jan | **New Year's Day**: New Year shows 15:00–19:00 |

The season's last date moves from 31 Dec to 1 Jan 2027.

## Saturday Special (18:00, every December Saturday)

**Every song in one block**, instead of the usual 18:00 show (Set B). The 17:00, 19:00 and 20:00 shows stay as normal.

Proposed running order, about 29 minutes. All nine songs run 26:16 together, plus skits and 4 s pauses:

| | Piece |
|---|---|
| | **Special intro** (new skit): Holly: "Welcome to the Saturday Special! Every song we know!" Jingle: "EVERY song?!" Ivy: "Especially that one." |
| 1 | Rockin' Around the Christmas Tree |
| 2 | Feliz Navidad |
| 3 | Dominick the Donkey |
| 4 | Frosty the Snowman |
| | Bramble falls asleep |
| 5 | Little Drummer Boy *(Bramble asleep)* |
| 6 | Twelve Days of Christmas *(still asleep)* |
| | **Bramble wakes up (special)** (new skit): "He slept through TWO songs!" "I was resting my eyes. Twice." |
| 7 | O Come All Ye Faithful |
| 8 | The Virgin Mary Had a Baby Boy |
| 9 | We Wish You a Merry Christmas |
| | **Thank you (special)** (new skit) |

Bramble's arc carries over: both "sleepy" songs sit between him falling asleep and waking. The set-list test should allow two in a row.

Announcing it ("that day and the week before"):

| When | What changes |
|---|---|
| Saturday, 16:15–16:45 | Announcements say "next show at five, **and at six it's the Saturday Special!**" (new: `announce-17-sat`) |
| Saturday, 17:15–17:45 | "**The Saturday Special starts at six: every song!**" (new: `announce-special`, replacing `announce-18`) |
| Saturday, 17:00 show | Its thank-you plugs the special at six (new: `thank-you-sat`) |
| Sun–Fri, up to 25 Dec | Every show's thank-you adds "**and this Saturday at six: the Saturday Special!**" (new: `thank-you-week`) |
| 27–30 Dec | Thank-yous plug New Year's Eve instead: "We're staying up till midnight!" (new: `thank-you-nye`) |

The Show A/B/C playlists therefore come in thank-you variants (normal, Saturday, week, NYE), generated rather than hand-made.

## New Year's Eve (Thu 31 Dec): to the midnight countdown

| Time | What plays |
|---|---|
| 16:00–23:58 | Waiting loop, with announcements as usual (the 19:xx ones announce "more shows later tonight") |
| 17:00, 18:00, 19:00, 20:00 | Normal shows (Sets A, B, C, A), thank-you plugs "see you at midnight!" |
| 22:00 | Set B |
| 23:15 | **NYE show**: new skit **Bramble's staying up**. Holly: "Bramble's going to stay awake until midnight." Bramble: "Easy." Then two or three songs. Bramble nods off during the last one. |
| 23:59:00 | **Countdown** (highest priority): 50 s of build-up, everyone counting **10…1** from 23:59:50, "**Happy New Year!**" at 00:00:00, and Bramble waking on the bang. Then **Auld Lang Syne**, with Noel holding the last "syyyyne". |
| about 00:06 | **Goodnight (New Year)**: "See you next year!", then dark. No 21:00 goodnight that night. |

Things to get right:
- **The clock.** FPP starts the countdown on its own clock, so the Pi needs internet time that night. At home the site router's WAN can plug into the home network. Check the time on FPP's Status page before 23:00. If the clock might be off, the countdown is the only thing that would be wrong.
- **An entry crossing midnight** (23:59 start, 00:09 end): check that FPP 10.3 handles an end time earlier than the start time on the bench. If not, split it at 23:59:59.
- **Volume after 23:00.** Neighbours. A quieter level for the late shows, or a word with them beforehand.

## New Year's Day (Fri 1 Jan): afternoon into evening

Shows at **15:00, 16:00, 17:00, 18:00 and 19:00** (sunset is about 16:05, so most run in the dark), the waiting loop in between, then a **"see you next Christmas"** goodnight at about 19:30.

**New Year music**: one set of about 4 songs (around 12 minutes), no Christmas songs. Rob picks the songs and supplies the MP3s. Suggestions that would lip-sync well:

| Song | Why |
|---|---|
| Auld Lang Syne | Shared with the midnight countdown, so it's built once |
| Happy New Year (ABBA) | The obvious one, slow and clear for mouths |
| Celebration (Kool & the Gang) | Big chorus for the whole choir |
| What a Wonderful World | Gentle; Bramble manages to stay awake for it |
| Walking on Sunshine / Here Comes the Sun | Bright for a January afternoon |

New skits: **New Year intro** (Pip's New Year joke; Bramble: "Is it still Christmas?"), **thank-you (New Year)**, and **goodnight (season)**: "See you next Christmas!"

## Building it

New pieces:
- **Skits**: special intro, Bramble wakes (special), thank-you variants (sat, week, nye, special, New Year), announce-17-sat, announce-special, Bramble's staying up, the countdown, goodnight (New Year), New Year intro, goodnight (season). About 15 short scripts; the ElevenLabs cost is small, under 3,000 characters.
- **Songs**: Auld Lang Syne, plus 3–4 New Year songs, each going through the per-song checklist (lyric timing, beats, sequence, arrangement, render check).
- **Countdown sequence**: lights and a choir-wide burst on the stroke of midnight, with the countdown voices.
- **Generator** (tools/gen_site_config.py): Saturday-only entries (day 6) and the normal 18:00 show on Sun–Fri (FPP day mask `0x17E00` = INX_DAY_MASK + every day but Saturday; constants from FPP 10.3 `src/ScheduleEntry.h`), dated entries for 31 Dec and 1 Jan, playlist variants, the season extended to 1 Jan, and tests for the priority and dates.
- **show-plan.md** will then list each kind of night.

Order, given 1 Dec is the deadline for the six trees: **Saturday Special first** (the first one is Sat 5 Dec), then New Year's Eve, then New Year's Day (the music needs Rob's picks first).
