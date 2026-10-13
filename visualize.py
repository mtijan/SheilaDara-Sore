"""Render conventional SVG bar charts from aggregate analysis metrics."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from xml.sax.saxutils import escape

from analysis import run

WIDTH, HEIGHT = 900, 350
LEFT, PLOT_WIDTH = 255, 540
BLUE, GRAY = "#2364AA", "#8291A0"
INK, MUTED, GRID = "#23313F", "#526170", "#DCE3E9"


def decimal(value: float, digits: int = 2) -> str:
    return f"{value:,.{digits}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def integer(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def bar_chart(
    chart_id: str,
    title: str,
    description: str,
    rows: list[tuple[str, float, str]],
    axis_max: float,
    tick_step: float,
    unit: str,
    note: str,
    *,
    percent: bool = False,
    decimals: int = 0,
) -> str:
    """Draw two bars on one zero-based axis with units, ticks and data labels."""
    if axis_max <= 0 or tick_step <= 0 or len(rows) != 2:
        raise ValueError("Two comparable rows and positive axis bounds are required")
    if any(value < 0 or value > axis_max for _, value, _ in rows):
        raise ValueError("Bar value is outside the axis")

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="{chart_id}-title {chart_id}-desc">',
        f'  <title id="{chart_id}-title">{escape(title)}</title>',
        f'  <desc id="{chart_id}-desc">{escape(description)}</desc>',
        f'  <rect width="{WIDTH}" height="{HEIGHT}" fill="#FFFFFF"/>',
        f'  <text x="36" y="42" fill="{INK}" font-size="23" font-weight="600" font-family="Arial, sans-serif">{escape(title)}</text>',
        f'  <text x="{LEFT}" y="81" fill="{MUTED}" font-size="13" font-family="Arial, sans-serif">{escape(unit)}</text>',
    ]
    tick = 0.0
    while tick <= axis_max + 1e-9:
        x = LEFT + PLOT_WIDTH * tick / axis_max
        tick_text = (decimal(tick, 0) if percent else integer(round(tick))) + ("%" if percent else "")
        parts.extend([
            f'  <line x1="{x:.1f}" y1="96" x2="{x:.1f}" y2="256" stroke="{GRID}" stroke-width="1"/>',
            f'  <text x="{x:.1f}" y="282" text-anchor="middle" fill="{MUTED}" font-size="13" font-family="Arial, sans-serif">{tick_text}</text>',
        ])
        tick += tick_step
    for index, (label, value, color) in enumerate(rows):
        y = 120 + index * 82
        width = PLOT_WIDTH * value / axis_max
        value_text = decimal(value, decimals) if decimals else integer(round(value))
        if percent:
            value_text += "%"
        parts.extend([
            f'  <text x="36" y="{y + 23}" fill="{INK}" font-size="16" font-family="Arial, sans-serif">{escape(label)}</text>',
            f'  <rect x="{LEFT}" y="{y}" width="{width:.1f}" height="32" fill="{color}"/>',
            f'  <text x="{LEFT + width + 10:.1f}" y="{y + 23}" fill="{INK}" font-size="15" font-weight="600" font-family="Arial, sans-serif">{value_text}</text>',
        ])
    parts.extend([
        f'  <text x="36" y="322" fill="{MUTED}" font-size="14" font-family="Arial, sans-serif">{escape(note)}</text>',
        "</svg>",
    ])
    return "\n".join(parts) + "\n"


def quality_chart(summary: dict) -> str:
    audit = summary["audit"]
    raw, analyzed = audit["input_rows"], audit["analyzed_rows"]
    return bar_chart(
        "quality", "Dari data mentah ke observasi unik",
        f"{integer(raw)} baris sumber menjadi {integer(analyzed)} observasi. {integer(audit['source_url_variants'])} variasi URL merujuk ke {integer(summary['videos'])} video.",
        [("Baris sumber", raw, GRAY), ("Dianalisis", analyzed, BLUE)],
        max(12000, math.ceil(max(raw, analyzed) / 2000) * 2000),
        2000, "Jumlah baris / observasi",
        f"{integer(audit['source_url_variants'])} variasi URL = {integer(summary['videos'])} video; {integer(audit['dropped_missing_or_blank'])} tidak lengkap, {integer(audit['removed_duplicates_within_video'])} duplikat.",
    )


def mention_chart(summary: dict) -> str:
    total, mention = summary["audit"]["analyzed_rows"], summary["sheila_mentions"]
    return bar_chart(
        "mention", "Komentar yang menyebut Sheila",
        f"{integer(mention)} dari {integer(total)} observasi, atau {decimal(summary['sheila_share_pct'])}%, menyebut Sheila.",
        [("Menyebut Sheila", mention, BLUE), ("Komentar lain", total - mention, GRAY)],
        max(6000, math.ceil(max(mention, total - mention) / 1000) * 1000),
        1000, "Jumlah observasi",
        f"Dasar: {integer(total)} komentar setelah pembersihan dan deduplikasi.",
    )


def tokens_chart(summary: dict) -> str:
    sheila, other = summary["avg_tokens_sheila"], summary["avg_tokens_other"]
    if sheila is None or other is None:
        raise ValueError("Both comment groups are needed for the token chart")
    return bar_chart(
        "tokens", "Rata-rata panjang komentar",
        f"Komentar yang menyebut Sheila rata-rata {decimal(sheila)} token; komentar lain {decimal(other)} token.",
        [("Menyebut Sheila", sheila, BLUE), ("Komentar lain", other, GRAY)],
        max(30, math.ceil(max(sheila, other) / 5) * 5),
        5, "Rata-rata token per komentar",
        "Panjang komentar bukan ukuran kualitas pendapat.", decimals=2,
    )


def sentiment_chart(summary: dict) -> str:
    sheila = summary["sentiment_sheila_pct"]["pos"]
    other = summary["sentiment_other_pct"]["pos"]
    if sheila is None or other is None:
        raise ValueError("Both comment groups are needed for the sentiment chart")
    largest = max(sheila, other)
    axis_max = 35 if largest <= 35 else math.ceil(largest / 20) * 20
    return bar_chart(
        "sentiment", "Proporsi label positif berbasis aturan",
        f"Aturan memberi label positif pada {decimal(sheila)} persen komentar yang menyebut Sheila dan {decimal(other)} persen komentar lain. Belum divalidasi oleh manusia.",
        [("Menyebut Sheila", sheila, BLUE), ("Komentar lain", other, GRAY)],
        axis_max, 5 if axis_max <= 40 else 20, "Persentase dalam masing-masing kelompok",
        "Label dari aturan kata; belum diukur akurasi terhadap label manusia.",
        percent=True, decimals=2,
    )


def concentration_chart(summary: dict) -> str:
    top = summary["top5_video_share_pct"]
    top_n = min(5, summary["videos"])
    remaining = summary["videos"] - top_n
    return bar_chart(
        "concentration", "Konsentrasi komentar menurut video",
        f"{top_n} video teratas menyumbang {decimal(top)} persen observasi; {remaining} video lain {decimal(100 - top)} persen.",
        [(f"{top_n} video teratas", top, BLUE), (f"{remaining} video lainnya", 100 - top, GRAY)],
        100, 20, "Persentase dari seluruh observasi",
        "Video diurutkan berdasarkan jumlah observasi setelah deduplikasi.",
        percent=True, decimals=2,
    )


def write_charts(summary: dict, output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    charts = {
        "quality": quality_chart(summary),
        "concentration": concentration_chart(summary),
        "mention": mention_chart(summary),
        "tokens": tokens_chart(summary),
        "sentiment": sentiment_chart(summary),
    }
    paths = {}
    for name, svg in charts.items():
        path = output_dir / f"{name}.svg"
        path.write_text(svg, encoding="utf-8")
        paths[name] = path
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path(__file__).with_name("youtube_comments_3.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).with_name("assets"))
    args = parser.parse_args()
    for name, path in write_charts(run(args.input), args.output_dir).items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
