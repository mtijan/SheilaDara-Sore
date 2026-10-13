import unittest
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

from analysis import add_sentiment, canonical_video_id, prepare_comments, score_comment, summarize
from visualize import write_charts


class AnalysisTests(unittest.TestCase):
    def test_deduplicates_only_within_the_same_video(self):
        source = pd.DataFrame([
            {"username": "@Alice", "comment": "Bagus!", "link_video": "https://www.youtube.com/watch?v=AAAAAAAAAAA&pp=one"},
            {"username": "alice", "comment": "Bagus!", "link_video": "https://www.youtube.com/watch?v=AAAAAAAAAAA&pp=two"},
            {"username": "Alice", "comment": "Bagus!", "link_video": "https://youtu.be/BBBBBBBBBBB"},
            {"username": None, "comment": "Bagus!", "link_video": "https://youtu.be/CCCCCCCCCCC"},
        ])
        cleaned, audit = prepare_comments(source)
        self.assertEqual(len(cleaned), 2)
        self.assertEqual(audit["removed_duplicates_within_video"], 1)
        self.assertEqual(audit["source_url_variants"], 3)
        self.assertEqual(audit["dropped_missing_or_blank"], 1)
        self.assertEqual(cleaned["row_id"].nunique(), 2)

    def test_youtube_tracking_parameters_do_not_change_video_identity(self):
        first = canonical_video_id("https://www.youtube.com/watch?v=AAAAAAAAAAA&pp=search-one")
        second = canonical_video_id("https://youtu.be/AAAAAAAAAAA?t=10")
        self.assertEqual(first, second)
        with self.assertRaisesRegex(ValueError, "video ID"):
            canonical_video_id("https://example.com/watch?v=AAAAAAAAAAA")

    def test_negation_does_not_leak_through_the_sentence(self):
        self.assertLess(score_comment("tidak bagus", "tidak bagus"), 0)
        self.assertEqual(score_comment("tidak terlalu bagus, keren", "tidak terlalu bagus keren"), 0)
        self.assertGreater(score_comment("tidak ada cerita bagus", "tidak ada cerita bagus"), 0)
        self.assertLess(score_comment("kurang bagus", "kurang bagus"), 0)

    def test_summary_uses_other_comments_as_comparison_group(self):
        source = pd.DataFrame([
            {"username": "a", "comment": "Sheila bagus", "link_video": "https://youtu.be/AAAAAAAAAAA"},
            {"username": "b", "comment": "jelek", "link_video": "https://youtu.be/AAAAAAAAAAA"},
        ])
        cleaned, audit = prepare_comments(source)
        result = summarize(add_sentiment(cleaned), audit)
        self.assertEqual(result["sheila_mentions"], 1)
        self.assertEqual(result["sentiment_sheila_pct"]["pos"], 100)
        self.assertEqual(result["sentiment_other_pct"]["pos"], 0)
        self.assertEqual(result["positive_gap_vs_other_pp"], 100)

    def test_missing_schema_is_actionable(self):
        with self.assertRaisesRegex(ValueError, "link_video"):
            prepare_comments(pd.DataFrame({"username": ["a"], "comment": ["hi"]}))

    def test_visuals_use_the_same_summary_without_comment_text(self):
        source = pd.DataFrame([
            {"username": "private-user", "comment": "Sheila bagus", "link_video": "https://youtu.be/AAAAAAAAAAA"},
            {"username": "another-user", "comment": "jelek", "link_video": "https://youtu.be/AAAAAAAAAAA"},
        ])
        cleaned, audit = prepare_comments(source)
        summary = summarize(add_sentiment(cleaned), audit)
        with tempfile.TemporaryDirectory() as directory:
            paths = write_charts(summary, Path(directory))
            self.assertEqual(set(paths), {"quality", "concentration", "mention", "tokens", "sentiment"})
            for path in paths.values():
                content = path.read_text(encoding="utf-8")
                root = ET.fromstring(content)
                ns = "{http://www.w3.org/2000/svg}"
                self.assertEqual(root.attrib["role"], "img")
                self.assertGreaterEqual(len(root.findall(f"{ns}line")), 2)
                self.assertTrue(
                    any(node.text in {"0", "0%"} for node in root.findall(f"{ns}text"))
                )
                self.assertNotIn("private-user", content)
                self.assertNotIn("Sheila bagus", content)
            self.assertIn("50,00%", paths["mention"].read_text(encoding="utf-8"))
            self.assertIn("100,00%", paths["sentiment"].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
