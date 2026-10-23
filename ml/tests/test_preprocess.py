# ml/tests/test_preprocess.py
"""
Unit tests for the preprocessing pipeline.
"""

import pytest
from ml.pipeline.preprocess import clean_text, combine_text_features
import pandas as pd


def test_clean_text_strips_html():
    assert "<b>hello</b>" not in clean_text("<b>hello</b>")
    assert "hello" in clean_text("<b>hello</b>")


def test_clean_text_lowercases():
    assert clean_text("HELLO WORLD") == "hello world"


def test_clean_text_handles_none():
    assert clean_text(None) == ""


def test_combine_text_features():
    df = pd.DataFrame({
        "title": ["Software Engineer"],
        "description": ["We are hiring a Python developer"],
        "requirements": [None],
    })
    result = combine_text_features(df)
    assert isinstance(result, pd.Series)
    assert len(result) == 1
    assert "software engineer" in result.iloc[0]
    assert "python" in result.iloc[0]
