# ml/pipeline/clean_text.py
"""
NLP text cleaning, normalization, and linguistic feature extraction module.

Cleans and normalizes job advertisement text:
- Strips HTML markup, entities, and mojibake.
- Normalizes URLs, email addresses, and phone numbers with semantic tokens.
- Preserves linguistic signals (e.g. uppercase ratio for SHOUTING urgency, URL presence).
- Concatenates multiple text columns into a unified feature string.

Usage:
    from ml.pipeline.clean_text import clean_text, process_corpus_text
    df_cleaned = process_corpus_text(df)
"""

import sys
import re
import html
import unicodedata
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ml.config import TEXT_COLUMNS

logger = logging.getLogger(__name__)

# Precompiled regex patterns for speed
HTML_TAG_PATTERN = re.compile(r"<[^>]+>", re.IGNORECASE)
HTML_ENTITY_PATTERN = re.compile(r"&[a-z0-9]+;", re.IGNORECASE)
URL_PATTERN = re.compile(
    r"https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)",
    re.IGNORECASE,
)
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
PHONE_PATTERN = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
MULTIPLE_SPACES_PATTERN = re.compile(r"\s+")
SPECIAL_CHAR_PATTERN = re.compile(r"[^a-zA-Z0-9\s.,!?:;'\-]")


def extract_text_telemetry(text: str) -> Dict[str, Any]:
    """
    Extract linguistic signals before destructive cleaning.
    """
    if not isinstance(text, str) or not text.strip():
        return {
            "char_count": 0,
            "word_count": 0,
            "uppercase_ratio": 0.0,
            "has_url": 0,
            "has_email": 0,
            "exclamation_count": 0,
        }

    raw_len = len(text)
    alpha_chars = sum(1 for c in text if c.isalpha())
    uppercase_chars = sum(1 for c in text if c.isupper())
    uppercase_ratio = round(uppercase_chars / alpha_chars, 4) if alpha_chars > 0 else 0.0

    return {
        "char_count": raw_len,
        "word_count": len(text.split()),
        "uppercase_ratio": uppercase_ratio,
        "has_url": 1 if URL_PATTERN.search(text) else 0,
        "has_email": 1 if EMAIL_PATTERN.search(text) else 0,
        "exclamation_count": text.count("!"),
    }


def clean_text(
    text: str,
    replace_urls: bool = True,
    replace_emails: bool = True,
    lowercase: bool = True,
    strip_punctuation: bool = False
) -> str:
    """
    Apply comprehensive text cleaning pipeline to a raw string.

    Args:
        text: Raw input string
        replace_urls: If True, replaces hyperlinks with token '[URL]'
        replace_emails: If True, replaces emails with token '[EMAIL]'
        lowercase: Whether to convert text to lower case
        strip_punctuation: Whether to remove punctuation

    Returns:
        str: Cleaned, normalized string
    """
    if not isinstance(text, str) or not text:
        return ""

    # 1. Unescape HTML entities (e.g. &amp; -> &, &quot; -> ")
    text = html.unescape(text)

    # 2. Unicode normalization (NFKD decomposes ligatures, accented chars)
    text = unicodedata.normalize("NFKD", text)

    # 3. Strip HTML tags
    text = HTML_TAG_PATTERN.sub(" ", text)

    # 4. Normalize or mask URLs and Emails
    if replace_urls:
        text = URL_PATTERN.sub(" urltoken ", text)
    if replace_emails:
        text = EMAIL_PATTERN.sub(" emailtoken ", text)

    # 5. Mask telephone numbers
    text = PHONE_PATTERN.sub(" phonetoken ", text)

    # 6. Optional punctuation stripping
    if strip_punctuation:
        text = re.sub(r"[^\w\s]", " ", text)
    else:
        text = SPECIAL_CHAR_PATTERN.sub(" ", text)

    # 7. Normalize whitespace
    text = MULTIPLE_SPACES_PATTERN.sub(" ", text).strip()

    # 8. Lowercasing
    if lowercase:
        text = text.lower()

    return text


def process_corpus_text(
    df: pd.DataFrame,
    text_cols: Optional[List[str]] = None,
    create_combined_column: bool = True
) -> pd.DataFrame:
    """
    Apply text cleaning across all specified text columns in the DataFrame
    and construct a unified 'combined_text' representation for vectorization.

    Args:
        df: Input DataFrame with missing values handled
        text_cols: Columns to clean. Defaults to config.TEXT_COLUMNS
        create_combined_column: Whether to create 'combined_text'

    Returns:
        pd.DataFrame with cleaned text columns and 'combined_text'
    """
    df_out = df.copy()
    target_cols = [c for c in (text_cols or TEXT_COLUMNS) if c in df_out.columns]

    logger.info(f"Applying text normalization to columns: {target_cols}")

    # Clean each text column individually
    for col in target_cols:
        logger.info(f"Cleaning column: {col}")
        # Compute telemetry before cleaning if it's the description
        if col == "description":
            telemetry = df_out[col].apply(extract_text_telemetry)
            telemetry_df = pd.DataFrame(telemetry.tolist(), index=df_out.index)
            for t_col in telemetry_df.columns:
                df_out[f"desc_{t_col}"] = telemetry_df[t_col]

        df_out[col] = df_out[col].fillna("").astype(str).apply(clean_text)

    if create_combined_column and target_cols:
        logger.info("Constructing combined_text feature...")
        df_out["combined_text"] = df_out[target_cols].apply(
            lambda row: " ".join(v for v in row if v), axis=1
        )
        logger.info(
            f"combined_text constructed. Average word count: "
            f"{df_out['combined_text'].apply(lambda x: len(x.split())).mean():.1f} words"
        )

    return df_out


if __name__ == "__main__":
    sample = """
    <h1>URGENT: Data Entry Clerk Needed NOW!!!</h1>
    <p>Contact us at <a href="mailto:hiring@fakejob.com">hiring@fakejob.com</a>!</p>
    Visit our site at http://free-jobs-now.com to earn $5,000/week!
    """
    telemetry = extract_text_telemetry(sample)
    cleaned = clean_text(sample)
    print("--- Sample Clean Text Test ---")
    print("Raw Telemetry:", telemetry)
    print("Cleaned:", cleaned)
