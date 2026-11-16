# AGENTS.md - guidebooks

Guest guides for The Way Vacations, published with GitHub Pages at
`https://the-way-vacations.github.io/guidebooks/`. Read this before editing any guide.

## The one rule

**Edit `src/*.html`, never the built pages.** Each file in `src/` is the single source for one
property's guide. `build.py` turns it into one page per booking channel. Never create or edit
`pure-destination-airbnb.html` (or any `*-airbnb.html`) by hand: it is generated.

## Layout

```
src/pure-destination.html     source for the Pure DESTINation guide (all channels)
build.py                      builds _site/ and runs the Airbnb policy check
policy/airbnb-banned.txt      patterns that must never appear on an Airbnb page
index.html                    landing page, copied to _site/ unchanged
heaven-on-surf.html           not yet converted; copied to _site/ unchanged
.github/workflows/pages.yml   runs build.py, deploys _site/
_site/                        build output (git-ignored)
```

## How the template works

Content in a source file is shared by every channel unless it is wrapped in a channel block:

```html
<!-- @only direct -->Call or text us at ...<!-- @end -->
<!-- @only airbnb -->Message us anytime in the Airbnb app.<!-- @end -->
```

- `direct` = the direct-booking site and Vrbo. `airbnb` = Airbnb guests.
- Blocks can sit inline (inside a sentence or a `<div>`) or wrap whole sections.
- Blocks don't nest. Every `@only` needs its `@end`.
- Keep shared content shared. Use a block only where the wording must differ, usually as a
  pair (one `direct`, one `airbnb`) so neither page ends up with a gap.
- A fix to shared text (directions, wifi, appliances, beach, food, emergency numbers) is made
  once and reaches every channel.

## What build.py does

Run `python build.py` (Python 3, no dependencies). It:

1. Deletes and recreates `_site/`.
2. Copies every top-level file that isn't build machinery (`index.html`, `heaven-on-surf.html`, ...)
   into `_site/` unchanged, and adds `.nojekyll`.
3. For each `src/<name>.html`, writes one page per channel:
   - `_site/<name>.html` - `direct` blocks kept, `airbnb` blocks removed. Same URL as before the
     template existed, so existing links keep working.
   - `_site/<name>-airbnb.html` - `airbnb` blocks kept, `direct` blocks removed.
   It stops with an error on an unknown channel name or an unbalanced marker.
4. Policy check: scans each Airbnb page (HTML comments ignored) against every pattern in
   `policy/airbnb-banned.txt`, case-insensitive. Any match prints file, line and pattern, and
   the build exits 1.

Channels and output names live in the `CHANNELS` dict at the top of `build.py`. A new channel
(for example `vrbo`) needs an entry there, its own blocks in the sources, and optionally a
`policy/vrbo-banned.txt`.

## The Airbnb policy check

Airbnb's "Reasonable house rules and requests" policy (help articles 4168 and 4169) covers
bookings from 20 Nov 2026. Airbnb guests must not be sent:

- off-platform contact: phone, text, email, our website, direct-booking pitches
  (everything goes through Airbnb messaging);
- chores beyond the listing's checkout requests (take out trash, start the dishwasher, strip beds...);
- fees, fines, deposits, ID requests, or review requests;
- rules that aren't on the Airbnb listing's House rules.

`policy/airbnb-banned.txt` holds one regex per line (`#` starts a comment). When a new violation is
found, add a pattern so it can't come back. A pattern that blocks something legitimate can be
narrowed, never just deleted. The check catches wording, not meaning: also read the Airbnb page
whenever you change a rule, checkout step or house instruction, and keep it matching the Airbnb
listing (House rules text, Local Rules, checkout requests).

## Deploying

- Pull request: the workflow runs `build.py` (build and policy check) without deploying.
  A failed check blocks the merge.
- Push to `main`: build, check, then deploy `_site/` to Pages.
- Preview locally: `python build.py`, then open the files in `_site/`.

## Facts that must match elsewhere

The guides restate facts that also live in OwnerRez (listing house rules, checkout requests, the
Airbnb rental agreement) and on the in-unit signs. When one changes, change it everywhere.
Current Pure DESTINation values:

- Check-in 4:00 PM, check-out 10:00 AM
- Quiet hours 10 PM-7 AM; pool 10 AM-10 PM
- Dumpster: south side, next to the tennis court (turn right out the front door)
- Okaloosa County Sheriff non-emergency: (850) 651-7400
- Say "the Gulf" (never "Gulf of Mexico" or "Gulf of America")

## Converting another guide

To move `heaven-on-surf.html` onto the template: `git mv heaven-on-surf.html src/`, add channel
blocks for its contact lines and checkout text, run `python build.py`, and fix every policy hit.
Its URL stays the same and `heaven-on-surf-airbnb.html` appears next to it.
