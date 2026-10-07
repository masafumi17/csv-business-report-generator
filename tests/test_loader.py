"""
Unit tests for src/loader.py module.
"""

from pathlib import Path
import pytest
from src.loader import CSVLoadError, load_csv


def test_load_valid_csv():
    """Test reading a valid CSV file succeeds."""
    sample_path = Path("data/sample_sales.csv")
    df = load_csv(sample_path)
    assert not df.empty
    assert "注文日" in df.columns
    assert "売上金額" in df.columns


def test_load_non_existent_csv():
    """Test reading a non-existent CSV raises CSVLoadError."""
    with pytest.raises(CSVLoadError) as exc_info:
        load_csv("data/non_existent_file.csv")
    assert "指定されたファイルが見つかりません" in str(exc_info.value)


def test_load_empty_csv(tmp_path):
    """Test reading an empty CSV raises CSVLoadError."""
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("", encoding="utf-8")

    with pytest.raises(CSVLoadError) as exc_info:
        load_csv(empty_file)
    assert "ファイルが空です" in str(exc_info.value)
