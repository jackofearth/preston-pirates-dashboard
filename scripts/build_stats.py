#!/usr/bin/env python3
"""Convert GameChanger CSV exports in data/csv/ into data/stats.json.

Exports are the "Export stats" CSVs from the GC team stats page:
  season.csv            season totals
  game<N>.csv           one file per game (N = the GC game number)

Fielding is deliberately dropped. Glossary is kept per column.
Run:  python3 scripts/build_stats.py
"""
import csv, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_DIR = ROOT / "data" / "csv"
OUT = ROOT / "data" / "stats.json"


def num(v):
    """GC cell -> float/int/None. '-' and 'N/A' and '' become None."""
    v = (v or "").strip()
    if v in ("", "-", "N/A"):
        return None
    try:
        f = float(v)
    except ValueError:
        return v
    return int(f) if f.is_integer() and "." not in v else f


def ip_to_outs(v):
    """Baseball innings notation (4.1 = 4 and 1/3) -> outs."""
    if v is None:
        return 0
    whole, _, frac = str(v).partition(".")
    return int(whole) * 3 + int(frac or 0)


def outs_to_ip(o):
    return f"{o // 3}.{o % 3}"


def parse(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    sections = rows[0]
    header = rows[1]
    # section boundaries from row 1 labels
    starts = {}
    for i, lab in enumerate(sections):
        if lab.strip():
            starts[lab.strip()] = i
    order = sorted(starts.items(), key=lambda kv: kv[1])
    bounds = {}
    for k, (lab, s) in enumerate(order):
        e = order[k + 1][1] if k + 1 < len(order) else len(header)
        bounds[lab] = (s, e)
    glossary_row = next(r for r in rows if r and r[0].strip() == "Glossary")
    gloss = {}
    for lab, (s, e) in bounds.items():
        gloss[lab] = {}
        for i in range(s, e):
            cell = glossary_row[i] if i < len(glossary_row) else ""
            if "=" in cell:
                k, _, d = cell.partition("=")
                gloss[lab][k.strip()] = d.strip()
    players, totals = [], None
    for r in rows[2:]:
        if not r or r[0].strip() == "Glossary":
            break
        if not any(c.strip() for c in r):
            continue
        rec = {}
        for lab in ("Batting", "Pitching"):
            s, e = bounds[lab]
            rec[lab.lower()] = {header[i]: num(r[i]) for i in range(s, e)}
        if r[0].strip() == "Totals":
            totals = rec
            continue
        rec["number"] = r[0].strip() or None
        rec["last"] = r[1].strip()
        rec["first"] = r[2].strip()
        rec["name"] = f"{r[2].strip()} {r[1].strip()}"
        players.append(rec)
    return players, totals, gloss


def main():
    season_players, season_totals, gloss = parse(CSV_DIR / "season.csv")
    games = []
    for p in sorted(CSV_DIR.glob("game*.csv"), key=lambda x: int(re.findall(r"\d+", x.stem)[0])):
        gno = int(re.findall(r"\d+", p.stem)[0])
        pl, tot, _ = parse(p)
        games.append({"game": gno, "players": pl, "totals": tot})

    # ---- verification: per-game counting stats must add up to season ----
    problems = []
    bat_keys = ["PA", "AB", "H", "RBI", "R", "BB", "SO", "SB", "XBH", "TB", "QAB"]
    pit_keys = ["BF", "#P", "H", "R", "ER", "BB", "SO"]
    sums = {}
    for g in games:
        for pl in g["players"]:
            s = sums.setdefault(pl["name"], {"b": {}, "p": {}, "outs": 0})
            for k in bat_keys:
                s["b"][k] = s["b"].get(k, 0) + (pl["batting"].get(k) or 0)
            for k in pit_keys:
                s["p"][k] = s["p"].get(k, 0) + (pl["pitching"].get(k) or 0)
            s["outs"] += ip_to_outs(pl["pitching"].get("IP"))
    for pl in season_players:
        s = sums.get(pl["name"])
        if not s:
            problems.append(f"{pl['name']}: in season CSV but in no game CSV")
            continue
        for k in bat_keys:
            if (pl["batting"].get(k) or 0) != s["b"][k]:
                problems.append(f"{pl['name']} batting {k}: season {pl['batting'].get(k)} vs games {s['b'][k]}")
        for k in pit_keys:
            if (pl["pitching"].get(k) or 0) != s["p"][k]:
                problems.append(f"{pl['name']} pitching {k}: season {pl['pitching'].get(k)} vs games {s['p'][k]}")
        if ip_to_outs(pl["pitching"].get("IP")) != s["outs"]:
            problems.append(f"{pl['name']} IP: season {pl['pitching'].get('IP')} vs games {outs_to_ip(s['outs'])}")
    names = {p["name"] for p in season_players}
    for n in sums:
        if n not in names:
            problems.append(f"{n}: in a game CSV but not season CSV")

    # ---- warnings (do not fail the build): GC runs vs GameDay final scores ----
    # GC game number == GameDay round number (washed-out rounds are simply skipped).
    warnings = []
    gd_path = ROOT / "data" / "gameday.json"
    if gd_path.exists():
        gd = json.loads(gd_path.read_text())
        for g in games:
            m = next((x for x in gd["matches"] if x["round"] == g["game"]
                      and "Preston" in (x["home"], x["away"]) and x["status"] == "final"), None)
            if not m:
                warnings.append(f"Game {g['game']}: no final GameDay score found for round {g['game']}")
                continue
            home = m["home"] == "Preston"
            us, them = (m["home_score"], m["away_score"]) if home else (m["away_score"], m["home_score"])
            gc_us, gc_them = g["totals"]["batting"].get("R"), g["totals"]["pitching"].get("R")
            if gc_us != us or gc_them != them:
                warnings.append(f"Game {g['game']}: GameDay final {us}-{them}, "
                                f"GC player stats add up to {gc_us}-{gc_them}")
    tr = season_totals["batting"].get("R")
    pr = sum((p["batting"].get("R") or 0) for p in season_players)
    if tr != pr:
        warnings.append(f"Season totals row shows {tr} runs, individual players add up to {pr}")

    import datetime
    out = {
        "note": "Built by scripts/build_stats.py from GameChanger CSV exports. Fielding omitted.",
        "built": datetime.date.today().isoformat(),
        "warnings": warnings,
        "season": {"players": season_players, "totals": season_totals},
        "games": games,
        "glossary": gloss,
        "verification": {"ok": not problems, "problems": problems},
    }
    OUT.write_text(json.dumps(out, indent=1))
    print(f"players={len(season_players)} games={[g['game'] for g in games]}")
    if problems:
        print("VERIFICATION PROBLEMS:")
        for x in problems:
            print(" -", x)
        sys.exit(1)
    print("verification OK: all games add up to season totals")


if __name__ == "__main__":
    main()
