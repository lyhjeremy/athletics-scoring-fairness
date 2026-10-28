# Auditing the scoring tables

A test of whether World Athletics points mean the same thing in every event, using the points awarded to 6,400 elite performances from 2023 and 2024.

[Live site](https://lyhjeremy.github.io/athletics-scoring-fairness/) · [Write-up](https://lyhjeremy.github.io/athletics-scoring-fairness/overview/) · [Long-form notes](writeup.md)

Design and copy follow [these standards](https://github.com/lyhjeremy/lyhjeremy/blob/main/DESIGN_STANDARDS.md).

## Results

- The median WA score of each event's top 30 performances ranges over 68.5 points: from 1272 in the 5000 m (+24.5 against the cross-event norm of 1247.5) down to 1203.5 in the javelin (−44).
- A Kruskal-Wallis test rejects equal score distributions across the 16 events (H = 236, p ≈ 10⁻⁴²).
- Running events score higher at the top. Seven of the eight events above the norm are running events (the shot put is the exception); seven of the eight below it are jumps and throws (the 800 m is the exception).

<p align="center">
  <img src="figures/fairness_boxplots.png" alt="Horizontal box plots of the top-30 WA scores for each of 16 events, sorted by median and colored by discipline group, with distance and sprint events right of the dashed norm line and javelin and hammer furthest left." width="840">
</p>

## Method

1. `fetch_data.py` scrapes the World Athletics outdoor top lists: top 100 per event for 16 events, men and women, 2023 and 2024, with each mark's nationality and awarded WA points ("Results Score"). That is 6,400 performances.
2. `analyze.py` takes the 30 highest scores per event (sexes and seasons pooled, since WA points are designed to be comparable across both) and computes each event's median.
3. The cross-event norm is the median of the 16 event medians. Each event's deviation from it goes to `tables/fairness_by_event.csv`.
4. A Kruskal-Wallis H test (SciPy) checks whether the 16 top-30 distributions could come from the same distribution.

## Stack

Python, pandas, lxml, NumPy, SciPy, matplotlib. Static site on GitHub Pages. The write-up lets you pick a WA score and see which events' elite medians it clears; that chart and its sortable table are plain SVG and JavaScript reading the numbers in `tables/fairness_by_event.csv`.

## How to run

```bash
pip install -r requirements.txt
python fetch_data.py      # scrape WA top lists (mark, points, nationality) -> data/raw/ (git-ignored)
python analyze.py         # elite-ceiling comparison and Kruskal-Wallis -> figures/ and tables/
```

## Repo layout

| Path | What it is |
|---|---|
| `fetch_data.py` | Scrape World Athletics top lists: mark, WA points, nationality, per event |
| `analyze.py` | Compare each event's elite WA-point ceiling and test for equality |
| `figures/` | Elite-ceiling box plots and per-event deviation |
| `tables/fairness_by_event.csv` | Top-30 median and deviation from the norm for each event |
| `index.html`, `overview/` | The two pages of the site |
| `writeup.md` | Long-form notes |

## Limitations

- An event's elite scores reflect both the table's calibration and the depth of its current field. A thin field shows a lower ceiling even under a fair table, and this study can't separate the two. What the data supports is the narrower claim: equal points don't currently mean equal elite standing. Whether any one table is miscoded is a separate question, and answering it would need each table checked against a fixed frontier, such as the world record.
- The top 30 pools men and women, and two seasons is a short window.
- H and p come from the raw scrape, which is git-ignored, so only the per-event table is reproducible from the committed files.

## License

[MIT](LICENSE) © 2026 Jeremy Lee. Performance data from World Athletics top lists.
