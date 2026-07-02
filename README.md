# Auditing the Scoring Tables — Are They Actually Fair?

**The World Athletics tables claim 1200 points in the shot put equals 1200 points in the 100 m. Do the world's best actually score the same across events?**

> 🌐 **Overview:** https://lyhjeremy.github.io/athletics-scoring-fairness/

Every cross-event comparison in track & field — combined events, athlete-of-the-year
votes, "who's the GOAT" — rests on the WA scoring tables treating events
equivalently. This project tests that claim directly against the global elite:
**6,400 top performances across 16 events** (2023–24), each with the WA points it
was actually awarded, scraped from the World Athletics top lists.

<p align="center">
  <img src="figures/fairness_boxplots.png" alt="Elite WA-point ceiling by event" width="840">
</p>

## What it finds

- **The elite ceiling is not level.** The median WA score of each event's top-30
  performances ranges over **68 points** — from the **5000 m (+24 above the norm)**
  down to the **javelin (−44 below)**. A Kruskal-Wallis test rejects "all events
  equal" overwhelmingly (H = 236, p ≈ 10⁻⁴²).
- **Running scores higher than the field events, at the top.** Distance and middle
  distances (5000 m, 1500 m) sit highest; **throws and jumps — javelin, hammer,
  high jump — sit well below** the cross-event norm.
- So among the current elite, an equal WA-point total does *not* map to an equal
  standing within one's event: the same 1250 points is a merely-very-good javelin
  throw but a fairly ordinary 5000 m.

## The honest interpretation
An event's elite-score distribution reflects **two** things: how the table is
calibrated **and** how deep/competitive the event's current field is. A thinly
contested event (hammer, javelin) will show a lower ceiling even under a perfectly
fair table, simply because fewer athletes push its frontier. So this is best read as
*"equal points don't currently mean equal elite standing,"* not as proof the tables
are miscoded. To isolate the table itself you'd want per-mark calibration against a
fixed frontier — a natural next step. The gap is real; its cause is part table, part
talent pool, and the write-up says so.

## Run it
```bash
pip install -r requirements.txt
python fetch_data.py      # scrape WA top lists (mark + points + nationality) -> data/raw/
python analyze.py         # elite-ceiling comparison + Kruskal-Wallis -> figures/ + tables/
```

## Files
| Path | What it is |
|---|---|
| `fetch_data.py` | Scrape World Athletics top lists: mark, WA points, nationality, per event |
| `analyze.py` | Compare each event's elite WA-point ceiling; test for equality |
| `figures/` | Elite-ceiling box plots and per-event deviation |
| `tables/` | `fairness_by_event.csv` |

## License
[MIT](LICENSE) © 2026 Jeremy Lee · performance data from World Athletics top lists
