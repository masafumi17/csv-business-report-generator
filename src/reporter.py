"""
Report generation orchestrator module.
Coordinates CSV loading, validation, aggregation, and Excel file generation.
"""

from pathlib import Path
from typing import Callable, Optional
import pandas as pd

from src.aggregator import (
    aggregate_by_category,
    aggregate_by_date,
    aggregate_by_product,
    aggregate_by_sales_rep,
    aggregate_summary,
)
from src.excel_generator import generate_excel_report
from src.loader import load_csv
from src.validator import validate_sales_data


def generate_report(
    csv_path: str | Path,
    output_dir: str | Path,
    log_callback: Optional[Callable[[str], None]] = None,
) -> Path:
    """
    Orchestrate the full sales report processing workflow.

    Args:
        csv_path (str | Path): Path to input sales CSV file.
        output_dir (str | Path): Output directory for the Excel report.
        log_callback (Optional[Callable[[str], None]]): Optional callback for progress logging.

    Returns:
        Path: Output path of generated Excel report file.
    """
    def log(msg: str):
        if log_callback:
            log_callback(msg)

    # 1. Load CSV
    log("[1/4] CSVファイルを読み込み中...")
    raw_df = load_csv(csv_path)
    log(f"  -> Raw CSV 読み込み完了 ({len(raw_df)} 行)")

    # 2. Validate Data
    log("[2/4] データバリデーションおよびエラーチェックを実行中...")
    clean_df, error_df = validate_sales_data(raw_df)
    log(f"  -> 正常データ: {len(clean_df)} 件, エラー検出データ: {len(error_df)} 件")

    # 3. Aggregate Data
    log("[3/4] 多角的な売上集計を計算中...")
    summary_kpi = aggregate_summary(clean_df)
    rep_df = aggregate_by_sales_rep(clean_df)
    cat_df = aggregate_by_category(clean_df)
    product_df = aggregate_by_product(clean_df)
    daily_df = aggregate_by_date(clean_df)
    log("  -> 集計処理完了 (サマリー / 担当者別 / カテゴリ別 / 商品別 / 日別)")

    # 4. Generate Excel Report & Charts
    log("[4/4] Excelブックの作成・装飾・グラフ描画を実行中...")
    output_path = Path(output_dir) / "業務売上レポート.xlsx"
    saved_file = generate_excel_report(
        summary_data=summary_kpi,
        daily_df=daily_df,
        rep_df=rep_df,
        cat_df=cat_df,
        product_df=product_df,
        error_df=error_df,
        output_path=output_path,
    )
    log(f"[完了] レポート出力完了: {saved_file.resolve()}")

    return saved_file
