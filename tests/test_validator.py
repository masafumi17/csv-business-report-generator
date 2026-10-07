"""
Unit tests for src/validator.py module.
"""

import pandas as pd
import pytest
from src.validator import ValidationError, validate_sales_data


def test_validate_missing_columns():
    """Test DataFrame with missing columns raises ValidationError."""
    invalid_df = pd.DataFrame({"注文日": ["2026-03-01"], "担当者": ["佐藤"]})
    with pytest.raises(ValidationError) as exc_info:
        validate_sales_data(invalid_df)
    assert "必須の列が不足しています" in str(exc_info.value)


def test_validate_separates_clean_and_error_rows():
    """Test valid rows are separated from invalid rows correctly."""
    raw_df = pd.DataFrame({
        "注文日": ["2026-03-01", "invalid_date", "2026-03-02"],
        "注文番号": ["ORD-001", "ORD-002", "ORD-003"],
        "商品カテゴリ": ["電子機器", "オフィス用品", "ソフトウェア"],
        "商品名": ["モニター", "チェア", "会計ソフト"],
        "数量": [2, "invalid_qty", 1],
        "売上金額": [88000, 45000, "invalid_amount"],
        "担当者": ["佐藤", "鈴木", "高橋"],
    })

    clean_df, error_df = validate_sales_data(raw_df)

    assert len(clean_df) == 1
    assert clean_df.iloc[0]["注文番号"] == "ORD-001"
    assert clean_df.iloc[0]["数量"] == 2
    assert clean_df.iloc[0]["売上金額"] == 88000.0

    assert len(error_df) == 2
    assert "日付形式が不正です" in error_df.iloc[0]["エラー理由"] or "数量" in error_df.iloc[0]["エラー理由"]
    assert "売上金額" in error_df.iloc[1]["エラー理由"]
