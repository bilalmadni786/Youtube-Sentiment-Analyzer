from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from comment_import import read_comment_rows, write_comment_rows


class CommentImportTests(unittest.TestCase):
    def test_read_comment_rows_accepts_xquik_export_headers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "comments.csv"
            with path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=["Tweet Text", "Username", "Tweet Created At"],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "Tweet Text": "Bahut acha video",
                        "Username": "ada",
                        "Tweet Created At": "2026-07-01",
                    }
                )
                writer.writerow({"Tweet Text": "  ", "Username": "bea"})

            rows = read_comment_rows(path)

        self.assertEqual(
            rows,
            [
                {
                    "text": "Bahut acha video",
                    "author": "ada",
                    "created_at": "2026-07-01",
                }
            ],
        )

    def test_write_comment_rows_preserves_sentiment_results(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "output.csv"
            write_comment_rows(
                path,
                [
                    {
                        "text": "Great",
                        "author": "ada",
                        "created_at": "2026-07-01",
                        "sentiment_result": "Sentiment: Positive",
                    }
                ],
            )

            with path.open(newline="", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

        self.assertEqual(rows[0]["sentiment_result"], "Sentiment: Positive")

    def test_read_comment_rows_requires_text_column(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.csv"
            path.write_text("likes\n3\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "comment, text"):
                read_comment_rows(path)


if __name__ == "__main__":
    unittest.main()
