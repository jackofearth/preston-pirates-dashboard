#!/usr/bin/env python3
"""One-off seed of data/gameday.json from a manual read of the GameDay pages
(Regional North East, 2026/27) on 2 Nov 2026. scripts/scrape_gameday.py replaces it
on a schedule. Tuples: (home, away, home_score, away_score, venue, time, status)
status: F = final, U = upcoming, N = no result recorded (0-0, not FINAL)."""
import json
from pathlib import Path
OUT = Path(__file__).resolve().parent.parent / "data" / "gameday.json"
G, GS, GP = "Ganbu Djila Sports Park", "Elder Street Reserve", "Police Paddock"
CS, NP, WF = "Campbell Street Reserve", "Napier Park", "Wadsworth Field"
D = [
 ("2026-10-04", [("Preston","South East Warriors",5,4,G,"1:30 PM","F"),("Diamond Creek","Waverley",10,22,CS,"1:30 PM","F"),("Greensborough","Malvern Red",0,0,GS,"1:30 PM","N"),("Diamond Creek S5","Malvern Blue",2,13,CS,"4:00 PM","F")]),
 ("2026-10-11", [("Greensborough","Preston",13,2,GS,"1:30 PM","F"),("Diamond Creek","Malvern Blue",0,0,NP,"1:30 PM","N"),("Waverley","Malvern Red",17,10,NP,"1:30 PM","F"),("Diamond Creek S5","South East Warriors",2,15,CS,"4:00 PM","F")]),
 ("2026-10-18", [("Preston","Malvern Blue",21,11,G,"1:30 PM","F"),("Greensborough","Malvern Red",8,4,GS,"1:30 PM","F"),("Waverley","Diamond Creek S5",14,6,NP,"1:30 PM","F"),("South East Warriors","Diamond Creek",11,6,GP,"1:30 PM","F")]),
 ("2026-10-25", [("Diamond Creek","Malvern Red",0,0,CS,"1:30 PM","N"),("Waverley","South East Warriors",0,0,NP,"1:30 PM","N"),("Greensborough","Preston",0,0,GS,"2:00 PM","N"),("Diamond Creek S5","Malvern Blue",0,0,CS,"4:00 PM","N")]),
 ("2026-11-01", [("Waverley","Preston",4,0,NP,"1:30 PM","F"),("South East Warriors","Greensborough",0,5,GP,"1:30 PM","F"),("Malvern Blue","Diamond Creek",13,5,WF,"1:30 PM","F"),("Malvern Red","Diamond Creek S5",10,6,WF,"4:00 PM","F")]),
 ("2026-11-08", [("Preston","Diamond Creek S5",None,None,G,"1:30 PM","U"),("Greensborough","Diamond Creek",None,None,GS,"1:30 PM","U"),("Waverley","Malvern Blue",None,None,NP,"1:30 PM","U"),("South East Warriors","Malvern Red",None,None,GP,"1:30 PM","U")]),
 ("2026-11-15", [("Preston","Malvern Red",None,None,G,"1:30 PM","U"),("Waverley","Greensborough",None,None,NP,"1:30 PM","U"),("South East Warriors","Malvern Blue",None,None,GP,"1:30 PM","U"),("Diamond Creek S5","Diamond Creek",None,None,CS,"4:00 PM","U")]),
 ("2026-11-22", [("Preston","Diamond Creek",None,None,G,"1:30 PM","U"),("South East Warriors","Diamond Creek S5",None,None,GP,"1:30 PM","U"),("Malvern Blue","Greensborough",None,None,WF,"1:30 PM","U"),("Malvern Red","Waverley",None,None,WF,"4:00 PM","U")]),
 ("2026-11-29", [("Preston","Waverley",None,None,G,"1:30 PM","U"),("Diamond Creek","South East Warriors",None,None,CS,"1:30 PM","U"),("Malvern Blue","Malvern Red",None,None,WF,"1:30 PM","U"),("Diamond Creek S5","Greensborough",None,None,CS,"4:00 PM","U")]),
 ("2026-12-05", [("Preston","Greensborough",None,None,G,"7:30 PM","U")]),
 ("2026-12-06", [("South East Warriors","Diamond Creek S5",None,None,GP,"1:30 PM","U"),("Malvern Blue","Waverley",None,None,WF,"1:30 PM","U"),("Malvern Red","Diamond Creek",None,None,WF,"4:00 PM","U")]),
 ("2026-12-13", [("Diamond Creek","Greensborough",None,None,CS,"1:30 PM","U"),("Malvern Blue","South East Warriors",None,None,WF,"1:30 PM","U"),("Diamond Creek S5","Preston",None,None,CS,"4:00 PM","U"),("Malvern Red","Waverley",None,None,WF,"4:00 PM","U")]),
 ("2026-12-20", [("Preston","Diamond Creek S5",None,None,G,"1:30 PM","U"),("Greensborough","Malvern Blue",None,None,GS,"1:30 PM","U"),("Waverley","Diamond Creek",None,None,NP,"1:30 PM","U"),("South East Warriors","Malvern Red",None,None,GP,"1:30 PM","U")]),
 ("2027-01-17", [("Diamond Creek","Greensborough",None,None,CS,"1:30 PM","U"),("Waverley","Malvern Blue",None,None,NP,"1:30 PM","U"),("South East Warriors","Preston",None,None,GP,"1:30 PM","U"),("Diamond Creek S5","Malvern Red",None,None,CS,"4:00 PM","U")]),
 ("2027-01-24", [("Diamond Creek","South East Warriors",None,None,CS,"1:30 PM","U"),("Malvern Blue","Preston",None,None,WF,"1:30 PM","U"),("Diamond Creek S5","Waverley",None,None,CS,"4:00 PM","U"),("Malvern Red","Greensborough",None,None,WF,"4:00 PM","U")]),
 ("2027-01-31", [("Preston","Waverley",None,None,G,"1:30 PM","U"),("Greensborough","South East Warriors",None,None,GS,"1:30 PM","U"),("Malvern Blue","Diamond Creek S5",None,None,WF,"1:30 PM","U"),("Malvern Red","Diamond Creek",None,None,WF,"4:00 PM","U")]),
 ("2027-02-07", [("Diamond Creek","Preston",None,None,CS,"1:30 PM","U"),("South East Warriors","Waverley",None,None,GP,"1:30 PM","U"),("Malvern Red","Malvern Blue",None,None,WF,"1:30 PM","U"),("Diamond Creek S5","Greensborough",None,None,CS,"4:00 PM","U")]),
 ("2027-02-14", [("Greensborough","Waverley",None,None,GS,"1:30 PM","U"),("Malvern Blue","South East Warriors",None,None,WF,"1:30 PM","U"),("Diamond Creek","Diamond Creek S5",None,None,CS,"4:00 PM","U"),("Malvern Red","Preston",None,None,WF,"4:00 PM","U")]),
 ("2027-02-21", [("Greensborough","Diamond Creek S5",None,None,GS,"1:30 PM","U"),("Waverley","Diamond Creek",None,None,NP,"1:30 PM","U"),("Malvern Blue","Preston",None,None,WF,"1:30 PM","U"),("Malvern Red","South East Warriors",None,None,WF,"4:00 PM","U")]),
]
# GameDay "round" = order of playing weekends (Sat 5 Dec + Sun 6 Dec are one round)
rnd, last_wk, matches = 0, None, []
import datetime as dt
for date, ms in D:
    d = dt.date.fromisoformat(date)
    wk = (d - dt.timedelta(days=(d.weekday() + 1) % 7)).isoformat()  # week starting Sunday
    if date == "2026-12-05": wk = "2026-12-06"
    if wk != last_wk: rnd += 1; last_wk = wk
    for h, a, hs, as_, v, t, st in ms:
        matches.append({"round": rnd, "date": date, "time": t, "home": h, "away": a,
                        "home_score": hs, "away_score": as_, "venue": v,
                        "status": {"F": "final", "U": "upcoming", "N": "no_result"}[st]})
# Two 0-0 non-final games are counted on GameDay's ladder as wins (9 runs "for", nothing
# "against") to the team named here. The match page shows no score, so the dashboard
# labels them "not scored - ladder credits <team>" rather than calling them forfeits.
CREDIT = {("2026-10-04", "Greensborough", "Malvern Red"): "Greensborough",
          ("2026-10-11", "Diamond Creek", "Malvern Blue"): "Diamond Creek"}
for m in matches:
    m["ladder_credit"] = CREDIT.get((m["date"], m["home"], m["away"]))
ladder = [("Waverley",4,4,0,0,57,26,"100.00"),("Greensborough",4,4,0,0,35,6,"100.00"),
 ("Preston",4,2,2,0,28,32,"50.00"),("Malvern Blue",4,2,2,0,37,28,"50.00"),
 ("South East Warriors",4,2,2,0,30,18,"50.00"),("Diamond Creek",4,1,3,0,30,46,"25.00"),
 ("Malvern Red",4,1,3,0,24,31,"25.00"),("Diamond Creek S5",4,0,4,0,16,52,"0.00"),
 ("Upwey FTG",0,0,0,0,0,0,"0.00")]
out = {"competition": "Regional North East", "season": "2026/2027 Summer",
       "uploaded": "Mon 2-Nov-2026 14:39:11", "source": "GameDay (manual seed)",
       "matches": matches,
       "ladder": [dict(zip(["pos","team","p","w","l","d","for","against","pct"], (i+1,)+r)) for i, r in enumerate(ladder)]}
OUT.write_text(json.dumps(out, indent=1))
print(len(matches), "matches;", max(m["round"] for m in matches), "rounds")
