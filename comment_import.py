from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path

TEXT_ALIASES = (
    "comment",
    "comments",
    "text",
    "tweet text",
    "tweet_text",
    "tweettext",
    "body",
    "message",
    "content",
)
AUTHOR_ALIASES = ("author", "username", "user", "channel", "x username")
DATE_ALIASES = (
    "created at",
    "created_at",
    "createdat",
    "tweet created at",
    "tweet_created_at",
    "tweetcreatedat",
    "date",
    "timestamp",
)


def normalize_column_name(column_name: object) -> str:
    return "".join(
        character
        for character in str(column_name).strip().lower()
        if character.isalnum()
    )


def find_column(columns: Iterable[object], aliases: Iterable[str]) -> str | None:
    normalized_aliases = {normalize_column_name(alias) for alias in aliases}
    for column in columns:
        if normalize_column_name(column) in normalized_aliases:
            return str(column)
    return None


def read_comment_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError("CSV must include a header row.")
        text_column = find_column(reader.fieldnames, TEXT_ALIASES)
        if text_column is None:
            raise ValueError(
                "CSV must include a comment, text, Tweet Text, or body column."
            )
        author_column = find_column(reader.fieldnames, AUTHOR_ALIASES)
        date_column = find_column(reader.fieldnames, DATE_ALIASES)

        rows = []
        for row in reader:
            text = (row.get(text_column) or "").strip()
            if not text:
                continue
            rows.append(
                {
                    "text": text,
                    "author": (row.get(author_column) or "Imported").strip()
                    if author_column
                    else "Imported",
                    "created_at": (row.get(date_column) or "").strip()
                    if date_column
                    else "",
                }
            )

    if not rows:
        raise ValueError("CSV must include at least one non-empty comment row.")
    return rows


def write_comment_rows(path: str | Path, rows: list[dict[str, str]]) -> None:
    fieldnames = ["text", "author", "created_at", "sentiment_result"]
    with Path(path).open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
