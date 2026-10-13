import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

from analysis import add_sentiment, prepare_comments


ROOT = Path(__file__).resolve().parents[1]


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = pd.read_csv(ROOT / "youtube_comments_3.csv")
        cleaned, _ = prepare_comments(source)
        cls.data = add_sentiment(cleaned)

    def test_report_covers_every_video_and_comment_once(self):
        report = pd.read_csv(ROOT / "reports/video_summary.csv")
        expected = self.data.groupby("video_id").size()
        actual = report.set_index("video_id")["komentar"]
        self.assertEqual(actual.to_dict(), expected.to_dict())
        self.assertEqual(int(report["komentar"].sum()), len(self.data))

    def test_review_ids_match_the_current_source(self):
        source_ids = set(self.data["row_id"])
        for filename, expected_rows in [
            ("question_spotcheck.csv", 35),
            ("sentiment_spotcheck.csv", 36),
        ]:
            review = pd.read_csv(ROOT / "reviews" / filename)
            self.assertEqual(len(review), expected_rows)
            self.assertTrue(review["row_id"].is_unique)
            self.assertTrue(set(review["row_id"]).issubset(source_ids))
            self.assertNotIn("comment_raw", review.columns)

    def test_saved_notebook_charts_match_svg_assets(self):
        notebook = json.loads((ROOT / "Sheila_Dara_Sore_YT_Sentiment.ipynb").read_text(encoding="utf-8"))
        seen = set()
        for cell in notebook["cells"]:
            for output in cell.get("outputs", []):
                svg_data = output.get("data", {}).get("image/svg+xml")
                if svg_data is None:
                    continue
                svg = "".join(svg_data)
                root = ET.fromstring(svg)
                title = root.find("{http://www.w3.org/2000/svg}title")
                chart_name = title.attrib["id"].removesuffix("-title")
                self.assertEqual(svg, (ROOT / "assets" / f"{chart_name}.svg").read_text(encoding="utf-8"))
                seen.add(chart_name)
        self.assertEqual(seen, {"quality", "mention", "tokens", "sentiment", "concentration"})


if __name__ == "__main__":
    unittest.main()
