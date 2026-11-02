#!/usr/bin/env python3
"""Refresh data/gameday.json from GameDay (Regional North East 2026/27).

GameDay draws fixtures/results with JavaScript, so this uses Playwright (a headless
browser). Ladder is a plain HTML table. Needs:  pip install playwright && playwright install chromium

    python3 scripts/scrape_gameday.py            # writes data/gameday.json
    python3 scripts/scrape_gameday.py --test     # parser self-test, no network

If GameDay refuses the request the script exits non-zero and leaves the old file alone.
"""
import datetime as dt, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "gameday.json"
VENUES_OUT = ROOT / "data" / "venues.json"
BASE = "https://websites.mygameday.app/comp_info.cgi?c=0-12901-0-664271-0&pool=1"
ROUNDS_URL = BASE + "&a=ROUND&round=-1"
LADDER_URL = BASE + "&a=LADDER"

DATE_RE = re.compile(r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday), (\w+) (\d+), (\d{4})$")
TIME_RE = re.compile(r"^\d{1,2}:\d{2} (AM|PM)$")


def parse_matches(text):
    """Parse the innerText of the GameDay results/fixtures page into match dicts.

    Each match is, in order:  home, [score | 'vs'], ['FINAL'], away-or-score ... venue, 'Sun 4 Oct', time, 'MATCH CENTRE'
    Played:    Home / 5 / FINAL / Away / 4 / Venue / Sun 4 Oct / 1:30 PM
    Unplayed:  Home / vs / Away / Venue / Sun 8 Nov / 1:30 PM
    Unscored:  Home / 0 / Away / 0 / Venue / ...  (no FINAL)"""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    matches, date = [], None
    i = 0
    while i < len(lines):
        m = DATE_RE.match(lines[i])
        if m:
            date = dt.datetime.strptime(f"{m.group(2)} {m.group(3)} {m.group(4)}", "%B %d %Y").date()
            i += 1
            continue
        if date is None:
            i += 1
            continue
        # find the end of this match block (the time line after a short date line)
        j = i
        while j < len(lines) and not TIME_RE.match(lines[j]):
            j += 1
            if j - i > 12:
                break
        if j >= len(lines) or j - i > 12:
            i += 1
            continue
        block = lines[i:j + 1]
        home = block[0]
        if block[1] == "vs":
            away, hs, as_, status = block[2], None, None, "upcoming"
            venue = block[3]
        else:
            hs = int(block[1])
            rest = block[2:]
            final = bool(rest and rest[0] == "FINAL")
            if final:
                rest = rest[1:]
            away, as_, venue = rest[0], int(rest[1]), rest[2]
            status = "final" if final else "no_result"
        matches.append({"date": date.isoformat(), "time": block[-1], "home": home, "away": away,
                        "home_score": hs, "away_score": as_, "venue": venue, "status": status})
        i = j + 1
        if i < len(lines) and lines[i] == "MATCH CENTRE":
            i += 1
    return matches


def assign_rounds(matches):
    """GameDay rounds = playing weekends in order. A Saturday joins the following Sunday."""
    wk_of = lambda d: (d - dt.timedelta(days=(d.weekday() + 1) % 7))
    keys = []
    for m in matches:
        d = dt.date.fromisoformat(m["date"])
        if d.weekday() == 5:
            d += dt.timedelta(days=1)
        keys.append(wk_of(d))
    order = {k: n + 1 for n, k in enumerate(sorted(set(keys)))}
    for m, k in zip(matches, keys):
        m["round"] = order[k]


def self_test():
    sample = """Sunday, October 4, 2026
Preston
5
FINAL
South East Warriors
4
Ganbu Djila Sports Park
Sun 4 Oct
1:30 PM
MATCH CENTRE
Greensborough
0
Malvern Red
0
Elder Street Reserve
Sun 4 Oct
1:30 PM
MATCH CENTRE
Sunday, November 8, 2026
Preston
vs
Diamond Creek S5
Ganbu Djila Sports Park
Sun 8 Nov
1:30 PM
MATCH CENTRE
Saturday, December 5, 2026
Preston
vs
Greensborough
Ganbu Djila Sports Park
Sat 5 Dec
7:30 PM
MATCH CENTRE
Sunday, December 6, 2026
Malvern Blue
vs
Waverley
Wadsworth Field
Sun 6 Dec
1:30 PM
MATCH CENTRE"""
    ms = parse_matches(sample)
    assign_rounds(ms)
    assert len(ms) == 5, ms
    assert (ms[0]["home_score"], ms[0]["away_score"], ms[0]["status"]) == (5, 4, "final")
    assert ms[1]["status"] == "no_result" and ms[1]["away"] == "Malvern Red"
    assert ms[2]["status"] == "upcoming" and ms[2]["away"] == "Diamond Creek S5"
    assert ms[3]["round"] == ms[4]["round"], "Sat 5 Dec and Sun 6 Dec must share a round"
    assert ms[0]["round"] < ms[2]["round"] < ms[3]["round"]
    print("parser self-test OK")


def scrape_venues(browser, links):
    """Each GameDay venue page has an address and a 'View Venue in Google Maps' link."""
    out = {}
    for name, url in links.items():
        try:
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            maps = page.eval_on_selector_all("a[href*='maps.google.com']", "as => as.map(a => a.href)")
            text = page.inner_text("body")
            m = re.search(r"Venue Address\s*(.+?)\s*Map Reference", text, re.S)
            page.close()
            if maps:
                out[name] = {"address": " ".join(m.group(1).split()) if m else "",
                             "map": maps[0], "gameday": re.sub(r"&fID=\d+|round=\d+&", "", url)}
        except Exception as e:  # venues are a nicety, never fail the whole refresh
            print("venue skipped:", name, e)
    return out


def main():
    if "--test" in sys.argv:
        return self_test()
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(user_agent=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"))
        pg.goto(ROUNDS_URL, wait_until="networkidle", timeout=60000)
        try:
            pg.wait_for_selector("text=MATCH CENTRE", timeout=45000)
        except Exception:
            pass
        main_text = pg.inner_text("body")
        if "MATCH CENTRE" not in main_text:
            print("DEBUG: fixtures page had no matches. title=%r url=%s" % (pg.title(), pg.url))
            print("DEBUG: first 600 chars of page text:\n" + main_text[:600])
        uploaded = re.search(r"Last Uploaded:\s*(.+?)\s*\|", main_text)
        matches = parse_matches(main_text)
        venue_links = pg.eval_on_selector_all(
            "main a[href*='a=VENUE']", "as => as.map(a => [a.innerText.trim(), a.href])")
        venues = scrape_venues(b, dict(venue_links))
        pg.goto(LADDER_URL, wait_until="networkidle", timeout=60000)
        rows = pg.eval_on_selector_all("table.stats-table tbody tr",
                                       "rs => rs.map(r => [...r.children].map(c => c.innerText.trim()))")
        b.close()
    if len(matches) < 40 or len(rows) < 6:
        sys.exit(f"Refusing to overwrite: only {len(matches)} matches / {len(rows)} ladder rows parsed")
    assign_rounds(matches)
    old = json.loads(OUT.read_text()) if OUT.exists() else {}
    credit = {(m["date"], m["home"], m["away"]): m.get("ladder_credit") for m in old.get("matches", [])}
    for m in matches:
        m["ladder_credit"] = credit.get((m["date"], m["home"], m["away"]))
    ladder = [dict(zip(["pos", "team", "p", "w", "l", "d", "for", "against", "pct"],
                       [int(r[0])] + [r[1]] + [int(x) for x in r[2:8]] + [r[8]])) for r in rows]
    OUT.write_text(json.dumps({
        "competition": "Regional North East", "season": "2026/2027 Summer",
        "uploaded": uploaded.group(1) if uploaded else None, "source": "GameDay",
        "matches": matches, "ladder": ladder}, indent=1))
    if venues:
        old_v = json.loads(VENUES_OUT.read_text()) if VENUES_OUT.exists() else {"venues": {}}
        old_v["venues"].update(venues)
        old_v["source"] = "GameDay venue pages (View Venue in Google Maps)"
        VENUES_OUT.write_text(json.dumps(old_v, indent=1))
    print(f"wrote {len(matches)} matches, {len(ladder)} ladder rows, {len(venues)} venues")


if __name__ == "__main__":
    main()
