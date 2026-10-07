"""
Unit tests for src/aggregator.py module.
"""

import pandas as pd
from src.aggregator import (
    aggregate_by_category,
    aggregate_by_date,
    aggregate_by_product,
    aggregate_by_sales_rep,
    aggregate_summary,
)


def get_sample_clean_df():
    return pd.DataFrame({
        "注文日": ["2026-03-01", "2026-03-01", "2026-03-02"],
        "注文番号": ["ORD-001", "ORD-002", "ORD-003"],
        "商品カテゴリ": ["電子機器", "オフィス用品", "電子機器"],
        "商品名": ["4Kモニター", "チェア", "4Kモニター"],
        "数量": [2, 1, 3],
        "売上金額": [88000.0, 45000.0, 132000.0],
        "担当者": ["佐藤 拓也", "鈴木 恵美", "佐藤 拓也"],
    })


def test_aggregate_summary():
    """Test summary KPI calculation."""
    df = get_sample_clean_df()
    summary = aggregate_summary(df)

    assert summary["total_sales"] == 265000.0
    assert summary["total_quantity"] == 6
    assert summary["order_count"] == 3
    assert summary["avg_order_amount"] == round(265000.0 / 3, 2)


def test_aggregate_by_sales_rep():
    """Test sales rep aggregation."""
    df = get_sample_clean_df()
    rep_df = aggregate_by_sales_rep(df)

    assert len(rep_df) == 2
    top_rep = rep_df.iloc[0]
    assert top_rep["担当者"] == "佐藤 拓也"
    assert top_rep["売上金額"] == 220000.0
    assert top_rep["数量"] == 5


def test_aggregate_by_category():
    """Test category aggregation."""
    df = get_sample_clean_df()
    cat_df = aggregate_by_category(df)

    assert len(cat_df) == 2
    top_cat = cat_df.iloc[0]
    assert top_cat["商品カテゴリ"] == "電子機器"
    assert top_cat["売上金額"] == 220000.0


def test_aggregate_by_product():
    """Test product aggregation."""
    df = get_sample_clean_df()
    prod_df = aggregate_by_product(df)

    assert len(prod_df) == 2
    assert prod_df.iloc[0]["商品名"] == "4Kモニター"
    assert prod_df.iloc[0]["売上金額"] == 220000.0


def test_aggregate_by_date():
    """Test daily aggregation."""
    df = get_sample_clean_df()
    daily_df = aggregate_by_date(df)

    assert len(daily_df) == 2
    assert daily_df.iloc[0]["注文日"] == "2026-03-01"
    assert daily_df.iloc[0]["売上金額"] == 133000.0
    assert daily_df.iloc[0]["注文件数"] == 2
