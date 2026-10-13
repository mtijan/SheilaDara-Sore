"""Reproducible, exploratory analysis of the bundled YouTube comment export.

Sentiment scores and clusters are heuristics. They are not accuracy estimates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer


REQUIRED_COLUMNS = {"username", "comment", "link_video"}
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
SPACE_RE = re.compile(r"\s+")
PLAIN_RE = re.compile(r"[^\w\s]", re.UNICODE)
SHEILA_RE = re.compile(r"\bsheila\b", re.IGNORECASE)
EMOJI_RE = re.compile(
    "[\U0001F300-\U0001F6FF\U0001F900-\U0001F9FF"
    "\U0001F1E0-\U0001F1FF\u2600-\u27BF\U0001FA70-\U0001FAFF]"
)
VIDEO_ID_RE = re.compile(r"[A-Za-z0-9_-]{11}")

POSITIVE = {
    "bagus", "keren", "suka", "mantap", "natural", "gemes", "lucu",
    "mengena", "rapi", "cantik", "solid", "kocak", "bahagia", "seneng",
    "salut", "sukses", "terbaik", "bangga", "terharu", "happy",
}
NEGATIVE = {
    "jelek", "garing", "lebay", "nanggung", "lambat", "bosan", "bosen",
    "buruk", "kaku", "berantakan", "cringe", "payah", "melelahkan",
    "membosankan", "gaje", "gagal", "kecewa",
}
POSITIVE_PHRASES = {"akting natural", "alur rapi", "terima kasih"}
NEGATIVE_PHRASES = {"ending nanggung", "alur lambat", "plot bolong"}
NEGATIONS = {"tidak", "gak", "ga", "nggak", "tak", "tdk", "bukan", "kurang"}
INTENSIFIERS = {"banget", "bgt", "amat", "sangat"}
POSITIVE_EMOJI = {"❤", "💖", "💕", "😍", "😊", "😀", "😁", "🤩", "😂", "🙌", "👍", "🔥", "🤗", "😄", "😆", "✨", "🎉", "👏"}
NEGATIVE_EMOJI = {"😒", "😡", "😠", "😔", "😢", "😭", "👎", "🙄", "😑", "🤨", "☹", "😞", "😩", "😤"}
TOPIC_STOPWORDS = {
    "ada", "aja", "aku", "atau", "banget", "bgt", "buat", "dan", "dari",
    "dia", "di", "gak", "ga", "gw", "gue", "ini", "itu", "jadi", "juga",
    "kalo", "kalau", "kamu", "ke", "kita", "lagi", "mereka", "nya",
    "sama", "saya", "sih", "tapi", "the", "udah", "untuk", "ya", "yang",
    "yg",
}


def normalize_space(value: str) -> str:
    return SPACE_RE.sub(" ", value.strip())


def canonical_video_id(url: str) -> str:
    """Identify one YouTube video independent of tracking query parameters."""
    parsed = urlsplit(url)
    host = (parsed.hostname or "").lower()
    if host in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
        if parsed.path == "/watch":
            video = parse_qs(parsed.query).get("v", [""])[0]
        else:
            parts = parsed.path.strip("/").split("/")
            video = parts[1] if len(parts) == 2 and parts[0] in {"shorts", "live", "embed"} else ""
    elif host == "youtu.be":
        video = parsed.path.strip("/").split("/")[0]
    else:
        video = ""
    if not VIDEO_ID_RE.fullmatch(video):
        raise ValueError("link_video must contain a valid YouTube video ID")
    return video


def row_id(video_id: str, username: str, comment: str) -> str:
    """Stable key for annotation within this export; no source comment ID exists."""
    value = "\x1f".join((video_id, username, comment))
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def prepare_comments(source: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    data = source.copy()
    data.columns = data.columns.str.strip().str.lower()
    missing = REQUIRED_COLUMNS - set(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    input_rows = len(data)
    data = data.dropna(subset=list(REQUIRED_COLUMNS)).copy()
    for column in REQUIRED_COLUMNS:
        data[column] = data[column].astype(str).map(normalize_space)
    data["username"] = data["username"].str.removeprefix("@").str.casefold()
    data = data.loc[data[list(REQUIRED_COLUMNS)].ne("").all(axis=1)].copy()
    after_missing = len(data)
    data["video_id"] = data["link_video"].map(canonical_video_id)
    source_url_variants = int(data["link_video"].nunique())

    # YouTube tracking parameters can give one video several URLs in the export.
    data = data.drop_duplicates(subset=["video_id", "username", "comment"]).copy()
    data["comment_raw"] = data["comment"]
    data["comment_clean"] = data["comment_raw"].map(
        lambda value: normalize_space(URL_RE.sub(" ", value)).casefold()
    )
    data["comment_plain"] = data["comment_clean"].map(
        lambda value: normalize_space(PLAIN_RE.sub(" ", value))
    )
    data["token_len"] = data["comment_plain"].str.split().map(len)
    data["emoji_count"] = data["comment_clean"].map(
        lambda value: len(EMOJI_RE.findall(value))
    )
    data["has_question_mark"] = data["comment_clean"].str.contains("?", regex=False)
    data["has_sheila"] = data["comment_plain"].str.contains(SHEILA_RE)
    data["row_id"] = [
        row_id(video_id, username, comment)
        for video_id, username, comment in zip(
            data["video_id"], data["username"], data["comment_raw"]
        )
    ]
    data = data.reset_index(drop=True)
    audit = {
        "input_rows": input_rows,
        "source_url_variants": source_url_variants,
        "dropped_missing_or_blank": input_rows - after_missing,
        "removed_duplicates_within_video": after_missing - len(data),
        "analyzed_rows": len(data),
    }
    return data, audit


def score_comment(clean_text: str, plain_text: str) -> float:
    """Small lexicon baseline; negation covers the next two tokens only."""
    tokens = plain_text.split()
    score = 0.0
    negate_until = -1
    last_polarity = 0.0
    index = 0
    while index < len(tokens):
        word = tokens[index]
        if word in NEGATIONS:
            negate_until = index + 2
            last_polarity = 0.0
            index += 1
            continue
        if word in INTENSIFIERS:
            if last_polarity:
                score += 0.5 * last_polarity
            last_polarity = 0.0
            index += 1
            continue

        phrase = " ".join(tokens[index:index + 2])
        step = 2 if phrase in POSITIVE_PHRASES | NEGATIVE_PHRASES else 1
        if step == 2:
            polarity = 2.0 if phrase in POSITIVE_PHRASES else -2.0
        elif word in POSITIVE:
            polarity = 1.0
        elif word in NEGATIVE:
            polarity = -1.0
        else:
            polarity = 0.0
        if polarity and index <= negate_until:
            polarity = -polarity
            negate_until = -1
        score += polarity
        last_polarity = polarity
        index += step

    # Cap repeated emoji so a copied sequence cannot dominate the word score.
    emoji_score = sum(1 for ch in clean_text if ch in POSITIVE_EMOJI)
    emoji_score -= sum(1 for ch in clean_text if ch in NEGATIVE_EMOJI)
    return score + max(-3, min(3, emoji_score))


def add_sentiment(data: pd.DataFrame) -> pd.DataFrame:
    result = data.copy()
    result["sentiment_score"] = [
        score_comment(clean, plain)
        for clean, plain in zip(result["comment_clean"], result["comment_plain"])
    ]
    result["sentiment_label"] = result["sentiment_score"].map(
        lambda value: "pos" if value > 0 else "neg" if value < 0 else "neu"
    )
    return result


def summarize(data: pd.DataFrame, audit: dict) -> dict:
    if data.empty:
        raise ValueError("No usable comments remain after cleaning")
    sheila = data.loc[data["has_sheila"]]
    other = data.loc[~data["has_sheila"]]

    def distribution(frame: pd.DataFrame) -> dict:
        return {
            label: round(100 * frame["sentiment_label"].eq(label).mean(), 2)
            if len(frame) else None
            for label in ("pos", "neg", "neu")
        }

    global_sentiment = distribution(data)
    sheila_sentiment = distribution(sheila)
    other_sentiment = distribution(other)
    result = {
        "audit": audit,
        "videos": int(data["video_id"].nunique()),
        "unique_usernames": int(data["username"].nunique()),
        "sheila_mentions": int(data["has_sheila"].sum()),
        "sheila_share_pct": round(100 * data["has_sheila"].mean(), 2),
        "question_mark_pct": round(100 * data["has_question_mark"].mean(), 2),
        "emoji_comment_pct": round(100 * data["emoji_count"].gt(0).mean(), 2),
        "avg_tokens_sheila": round(sheila["token_len"].mean(), 2) if len(sheila) else None,
        "avg_tokens_other": round(other["token_len"].mean(), 2) if len(other) else None,
        "median_tokens_sheila": int(sheila["token_len"].median()) if len(sheila) else None,
        "median_tokens_other": int(other["token_len"].median()) if len(other) else None,
        "question_mark_sheila_pct": round(100 * sheila["has_question_mark"].mean(), 2) if len(sheila) else None,
        "question_mark_other_pct": round(100 * other["has_question_mark"].mean(), 2) if len(other) else None,
        "sentiment_global_pct": global_sentiment,
        "sentiment_sheila_pct": sheila_sentiment,
        "sentiment_other_pct": other_sentiment,
        "positive_gap_vs_other_pp": round(
            sheila_sentiment["pos"] - other_sentiment["pos"], 2
        ) if len(sheila) and len(other) else None,
    }
    if "publish_date" in data:
        # This is metadata for the source videos, not the collection date.
        dates = pd.to_datetime(data["publish_date"], errors="coerce")
        result["video_publish_date_min"] = str(dates.min().date()) if dates.notna().any() else None
        result["video_publish_date_max"] = str(dates.max().date()) if dates.notna().any() else None

    top_five = data["video_id"].value_counts().head(5).sum()
    result["top5_video_share_pct"] = round(100 * top_five / len(data), 2)
    by_group = (
        data.assign(is_positive=data["sentiment_label"].eq("pos"))
        .groupby(["video_id", "has_sheila"])
        .agg(count=("row_id", "size"), positive_rate=("is_positive", "mean"), mean_tokens=("token_len", "mean"))
        .reset_index()
    )
    counts = by_group.pivot(index="video_id", columns="has_sheila", values="count").reindex(columns=[False, True]).fillna(0)
    eligible = counts.index[(counts[False] >= 10) & (counts[True] >= 10)]
    positive = by_group.pivot(index="video_id", columns="has_sheila", values="positive_rate").reindex(columns=[False, True])
    tokens = by_group.pivot(index="video_id", columns="has_sheila", values="mean_tokens").reindex(columns=[False, True])
    result["within_video_comparison"] = {
        "minimum_per_group": 10,
        "eligible_videos": len(eligible),
        "higher_positive_rate_videos": int((positive.loc[eligible, True] > positive.loc[eligible, False]).sum()),
        "higher_mean_tokens_videos": int((tokens.loc[eligible, True] > tokens.loc[eligible, False]).sum()),
    }
    return result


def discover_topics(data: pd.DataFrame, clusters: int = 10) -> list[dict]:
    """Return numeric clusters and term signatures, without invented topic names."""
    eligible = data.loc[data["token_len"] >= 2].copy()
    if len(eligible) < clusters:
        raise ValueError("Not enough comments for the requested number of clusters")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2), min_df=2, max_df=0.9, max_features=10000,
        sublinear_tf=True, stop_words=sorted(TOPIC_STOPWORDS),
    )
    matrix = vectorizer.fit_transform(eligible["comment_plain"])
    model = KMeans(n_clusters=clusters, random_state=42, n_init=10)
    eligible["cluster_id"] = model.fit_predict(matrix)
    terms = vectorizer.get_feature_names_out()
    result = []
    for cluster_id in range(clusters):
        subset = eligible.loc[eligible["cluster_id"] == cluster_id]
        top = model.cluster_centers_[cluster_id].argsort()[-8:][::-1]
        result.append({
            "cluster_id": cluster_id,
            "comments": len(subset),
            "share_of_clustered_pct": round(100 * len(subset) / len(eligible), 2),
            "sheila_mention_pct": round(100 * subset["has_sheila"].mean(), 2),
            "top_terms": [str(terms[index]) for index in top],
        })
    return result


def run(input_path: Path, clusters: int | None = None) -> dict:
    source = pd.read_csv(input_path)
    cleaned, audit = prepare_comments(source)
    scored = add_sentiment(cleaned)
    result = summarize(scored, audit)
    if clusters is not None:
        result["topic_exploration"] = discover_topics(scored, clusters)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path(__file__).with_name("youtube_comments_3.csv"))
    parser.add_argument("--clusters", type=int, help="Also compute exploratory K-Means clusters")
    parser.add_argument("--output", type=Path, help="Write aggregate JSON; never exports comment text")
    args = parser.parse_args()
    if args.clusters is not None and args.clusters < 2:
        parser.error("--clusters must be at least 2")
    result = run(args.input, args.clusters)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
