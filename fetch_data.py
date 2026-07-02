"""Download World Athletics top-lists (elite performances + their WA points).

The WA site renders its top-lists server-side as HTML tables that include, for each
performance, the **mark**, the athlete's **nationality**, and the **WA points**
("Results Score") — everything needed to audit whether the scoring tables treat
events equivalently. We pull the top 100 of each event for two recent, clean
seasons (all legal marks) across the standard event programme.

Output: data/raw/toplists.csv  (event, category, gender, year, rank, mark, score, nat, date)

Usage:  python fetch_data.py
"""

from __future__ import annotations

import io
import time
from pathlib import Path

import pandas as pd
import urllib.request

RAW = Path(__file__).resolve().parent / "data" / "raw"
UA = {"User-Agent": "Mozilla/5.0 (athletics-scoring-fairness research; github.com/lyhjeremy)"}
YEARS = [2023, 2024]
BASE = "https://www.worldathletics.org/records/toplists/{cat}/{ev}/outdoor/{g}/senior/{yr}?page=1"

# (event key, WA category slug, WA event slug, discipline group)
EVENTS = [
    ("100m", "sprints", "100-metres", "sprint"),
    ("200m", "sprints", "200-metres", "sprint"),
    ("400m", "sprints", "400-metres", "sprint"),
    ("800m", "middlelong", "800-metres", "middle"),
    ("1500m", "middlelong", "1500-metres", "middle"),
    ("5000m", "middlelong", "5000-metres", "distance"),
    ("10000m", "middlelong", "10000-metres", "distance"),
    ("marathon", "road-running", "marathon", "distance"),
    ("high_jump", "jumps", "high-jump", "jump"),
    ("pole_vault", "jumps", "pole-vault", "jump"),
    ("long_jump", "jumps", "long-jump", "jump"),
    ("triple_jump", "jumps", "triple-jump", "jump"),
    ("shot_put", "throws", "shot-put", "throw"),
    ("discus", "throws", "discus-throw", "throw"),
    ("hammer", "throws", "hammer-throw", "throw"),
    ("javelin", "throws", "javelin-throw", "throw"),
]


def _scrape(cat, ev, g, yr) -> pd.DataFrame:
    url = BASE.format(cat=cat, ev=ev, g=g, yr=yr)
    html = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode("utf-8", "replace")
    tabs = [t for t in pd.read_html(io.StringIO(html)) if t.shape[0] > 10 and "Mark" in t.columns]
    if not tabs:
        return pd.DataFrame()
    t = tabs[0]
    # nationality is the first unnamed column after Competitor; score is "Results Score".
    nat_col = next((c for c in t.columns if str(c).startswith("Unnamed")), None)
    out = pd.DataFrame({
        "rank": pd.to_numeric(t["Rank"], errors="coerce"),
        "mark": t["Mark"].astype(str),
        "score": pd.to_numeric(t.get("Results Score"), errors="coerce"),
        "nat": t[nat_col].astype(str) if nat_col else "",
        "date": t.get("Date", "").astype(str),
    })
    return out.dropna(subset=["score"])


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    frames = []
    for key, cat, ev, grp in EVENTS:
        for g in ("men", "women"):
            for yr in YEARS:
                try:
                    d = _scrape(cat, ev, g, yr)
                except Exception as e:
                    print(f"  ! {key:12s} {g} {yr}: {type(e).__name__}")
                    continue
                if d.empty:
                    continue
                d.insert(0, "event", key); d.insert(1, "category", grp)
                d.insert(2, "gender", "M" if g == "men" else "W"); d.insert(3, "year", yr)
                frames.append(d)
                time.sleep(0.8)
        got = sum(len(f) for f in frames if f["event"].iloc[0] == key)
        print(f"  {key:12s} {got:4d} performances (top score {max((f.score.max() for f in frames if f['event'].iloc[0]==key), default=0):.0f})")

    out = pd.concat(frames, ignore_index=True)
    out.to_csv(RAW / "toplists.csv", index=False)
    print(f"\nwrote data/raw/toplists.csv  ({len(out)} rows, {out.event.nunique()} events, {out.nat.nunique()} nations)")


if __name__ == "__main__":
    main()
