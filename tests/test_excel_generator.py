"""
Unit tests for src/excel_generator.py module.
"""

from pathlib import Path
import openpyxl
import pandas as pd
from src.excel_generator import generate_excel_report


def test_generate_excel_report(tmp_path):
    """Test generating full Excel report workbook with all required sheets."""
    summary_data = {
        "total_sales": 100000.0,
        "total_quantity": 5,
        "order_count": 2,
        "avg_order_amount": 50000.0,
    }
    daily_df = pd.DataFrame({"注文日": ["2026-03-01"], "売上金額": [100000.0], "注文件数": [2]})
    rep_df = pd.DataFrame({"担当者": ["佐藤"], "売上金額": [100000.0], "数量": [5], "売上構成比(%)": [100.0]})
    cat_df = pd.DataFrame({"商品カテゴリ": ["電子機器"], "売上金額": [100000.0], "数量": [5], "売上構成比(%)": [100.0]})
    product_df = pd.DataFrame({"商品名": ["モニター"], "商品カテゴリ": ["電子機器"], "売上金額": [100000.0], "数量": [5]})
    error_df = pd.DataFrame({"元行番号": [2], "注文日": ["2026-99-99"], "エラー理由": ["日付不正"]})

    out_file = tmp_path / "test_report.xlsx"
    saved = generate_excel_report(
        summary_data=summary_data,
        daily_df=daily_df,
        rep_df=rep_df,
        cat_df=cat_df,
        product_df=product_df,
        error_df=error_df,
        output_path=out_file,
    )

    assert saved.exists()
    wb = openpyxl.load_workbook(saved)
    expected_sheets = ["サマリー", "日別集計", "担当者別集計", "カテゴリ別集計", "商品別集計", "エラーデータ"]
    for s_name in expected_sheets:
        assert s_name in wb.sheetnames
