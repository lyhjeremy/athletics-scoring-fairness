"""Are the World Athletics scoring tables fair across events?

The tables promise that 1200 points in the shot put equals 1200 points in the
100 m. We test that against the global elite: for each event we take the WA points
("Results Score") that its very best recent performances actually reach, and ask
whether that elite ceiling is the same from event to event. Under fair tables it
should be; a systematic gap means an event is over- or under-rewarded.

Caveat we state plainly: an event's elite-score distribution reflects *both* the
table's calibration *and* how deep/competitive the event is. We therefore compare
the top slice (least depth-sensitive) and read differences as suggestive, not proof
of a table flaw.

Outputs: figures/*.png, tables/*.csv
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent
FIG, TAB = ROOT / "figures", ROOT / "tables"
TOP_N = 30                    # the elite ceiling per event
INK, GOLD, WINE, SKY = "#1a1a2e", "#D4A537", "#7a1f2b", "#4a7ba6"

LABELS = {
    "100m": "100 m", "200m": "200 m", "400m": "400 m", "800m": "800 m",
    "1500m": "1500 m", "5000m": "5000 m", "10000m": "10,000 m", "marathon": "Marathon",
    "high_jump": "High jump", "pole_vault": "Pole vault", "long_jump": "Long jump",
    "triple_jump": "Triple jump", "shot_put": "Shot put", "discus": "Discus",
    "hammer": "Hammer", "javelin": "Javelin",
}
CAT_COLOR = {"sprint": "#7a1f2b", "middle": "#b5651d", "distance": "#c99a3b",
             "jump": "#2a7f62", "throw": "#4a7ba6"}


def main() -> None:
    FIG.mkdir(exist_ok=True); TAB.mkdir(exist_ok=True)
    df = pd.read_csv(ROOT / "data" / "raw" / "toplists.csv")

    # Elite ceiling: the TOP_N highest WA scores in each event (pooling years/genders;
    # WA points are designed to be comparable across both).
    top = (df.sort_values("score", ascending=False)
             .groupby("event").head(TOP_N).copy())
    cats = df.groupby("event").category.first()

    med = top.groupby("event").score.median()
    grand = med.median()
    dev = (med - grand).sort_values()

    print(f"{len(df)} performances, {df.event.nunique()} events, {df.nat.nunique()} nations")
    print(f"grand median of elite (top-{TOP_N}) scores: {grand:.0f}")
    print(f"\nMost UNDER-rewarded (elite ceiling scores below the norm):")
    for ev, d in dev.head(3).items():
        print(f"  {LABELS[ev]:12s} median {med[ev]:.0f}  ({d:+.0f} vs norm)")
    print("Most OVER-rewarded:")
    for ev, d in dev.tail(3).items():
        print(f"  {LABELS[ev]:12s} median {med[ev]:.0f}  ({d:+.0f} vs norm)")
    spread = med.max() - med.min()
    print(f"\nspread between best- and worst-rewarded event: {spread:.0f} WA points "
          f"({LABELS[med.idxmax()]} vs {LABELS[med.idxmin()]})")

    # Do the elite score distributions actually differ across events?
    groups = [g.score.values for _, g in top.groupby("event")]
    H, p = stats.kruskal(*groups)
    print(f"Kruskal-Wallis across events: H={H:.0f}, p={p:.1e} "
          f"({'distributions differ' if p < 0.05 else 'no significant difference'})")

    out = pd.DataFrame({"event": [LABELS[e] for e in med.index], "category": cats[med.index].values,
                        "elite_median_score": med.values,
                        "deviation_vs_norm": (med - grand).values}).sort_values("deviation_vs_norm")
    out.to_csv(TAB / "fairness_by_event.csv", index=False)

    _figures(top, med, dev, grand, cats)


def _figures(top, med, dev, grand, cats):
    order = med.sort_values().index.tolist()

    # Fig 1: box plots of elite scores by event (sorted), coloured by discipline
    fig, ax = plt.subplots(figsize=(11, 6))
    data = [top[top.event == e].score.values for e in order]
    bp = ax.boxplot(data, vert=False, patch_artist=True, widths=0.62,
                    medianprops=dict(color=INK, lw=1.4), flierprops=dict(marker=".", ms=3, mfc="#aaa", mec="none"))
    for patch, e in zip(bp["boxes"], order):
        patch.set_facecolor(CAT_COLOR.get(cats[e], "#888")); patch.set_alpha(0.85); patch.set_edgecolor("white")
    ax.set_yticklabels([LABELS[e] for e in order])
    ax.axvline(grand, color=INK, ls="--", lw=1.3, label=f"cross-event norm ({grand:.0f})")
    ax.set_xlabel(f"WA points of each event's top-{TOP_N} performances (2023–24)")
    ax.set_title("Do equal WA points mean equal achievement? The elite ceiling, event by event",
                 fontweight="bold", fontsize=12.5)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(facecolor=c, label=k) for k, c in CAT_COLOR.items()] +
                      [plt.Line2D([0], [0], color=INK, ls="--", label=f"norm {grand:.0f}")],
              frameon=False, fontsize=8, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(FIG / "fairness_boxplots.png", dpi=150); plt.close(fig)

    # Fig 2: per-event deviation from the norm
    fig, ax = plt.subplots(figsize=(9, 6))
    colors = [WINE if v > 0 else SKY for v in dev.values]
    ax.barh([LABELS[e] for e in dev.index], dev.values, color=colors)
    ax.axvline(0, color=INK, lw=0.9)
    ax.set_xlabel("elite-ceiling deviation from the cross-event norm (WA points)")
    ax.set_title("Over- and under-rewarded events\n(positive = its best performances score above the norm)",
                 fontweight="bold", fontsize=12)
    for e, v in dev.items():
        ax.text(v + (0.6 if v >= 0 else -0.6), LABELS[e], f"{v:+.0f}",
                va="center", ha="left" if v >= 0 else "right", fontsize=8, color=INK)
    ax.margins(x=0.14)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(FIG / "deviation.png", dpi=150); plt.close(fig)
    print(f"\nwrote {len(list(FIG.glob('*.png')))} figures, {len(list(TAB.glob('*.csv')))} tables")


if __name__ == "__main__":
    main()
