# Preston Pirates dashboard

Stats, leaders, game-by-game trends, fixtures and ladder for the Preston Pirates (VSBL Regional North East 2026/27). A static site: `index.html` reads three JSON files in `data/`.

## Adding a new game (GameChanger stats)

1. In GameChanger, export the **season stats** CSV and the **game stats** CSV for the new game.
2. Put them in `data/csv/` as `season.csv` (replace the old one) and `gameN.csv`, where N is the round number (game 5 is `game5.csv`). Skip washed-out rounds.
3. Commit to `main`. The "Build stats" workflow runs `scripts/build_stats.py`, which checks that every game adds up to the season totals and refuses to build if it doesn't.

To run it yourself: `python3 scripts/build_stats.py`.

The game file must be a single game (GP 1), exported at the same time as the season file. A season export saved as a game file will not add up and the build will stop.

## Fixtures, results and ladder (GameDay)

`.github/workflows/refresh-gameday.yml` runs `scripts/scrape_gameday.py` every hour at :07 from Saturday 12:07pm to Tuesday 8:07pm Melbourne time, and twice a day (8:07am and 8:07pm) for the rest of the week and commits `data/gameday.json`. After the scraper self-test it also checks forfeit winners against GameDay's ladder. The window is set in UTC for Melbourne summer time (+11), so it slides an hour when daylight saving ends in April 2027. An alert issue is raised after 6 failed runs in a row. If GameDay blocks GitHub's servers the job fails and the old data stays. You can also run the workflow by hand from the Actions tab.

The scraper reads the match list GameDay embeds in the page (`var matches = [...]`), not the rendered text. "Washed Out" matches are not counted in the record; 0-0 results with a winner are shown as forfeits.

**GameDay data quirks (learned the hard way).** GameDay's `WinnerID` is a number and `HomeID` is text, so compare them as strings. For a forfeit GameDay's ladder gives the winner 9 runs For and adds nothing to anyone's Against (the playing conditions say 0-9). Results can be missing or briefly wrong (a forfeit placeholder was later replaced by the real score), so refresh before reasoning about the ladder, and treat un-entered games as unknown rather than assuming a winner. The scraper's self-test (`--test`) uses the real ID types, and every refresh recounts standings from the match list and corrects forfeit winners if they disagree with the ladder.

## Overview page notes

- **Next game rolls over 3 hours after the start time** (`GAME_HOURS` in `index.html`). Until GameDay has the score, the Last game panel says "Result pending"; the record and ladder only change when GameDay has the result.
- **Forecast** on the next-game card comes straight from the browser to [Open-Meteo](https://open-meteo.com/) (free, no key, about 16 days ahead). It uses the venue coordinates from `data/venues.json`. Rain is the total from 12 hours before the start to halfway through a 2-hour game. If the request fails the forecast is simply hidden.
- Last game shows that game's team AVG, QAB%, FIP and S% from its `gameN.csv`.

## Publishing

Settings → Pages → Deploy from a branch → `main` / root.

## Local preview

```
python3 -m http.server
```
