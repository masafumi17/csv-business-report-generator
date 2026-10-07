"""
Excel report generation module using openpyxl.
Formats worksheets, applies number styles, creates executive KPI summary cards,
and integrates visual charts into the final report.
"""

from pathlib import Path
from typing import Dict, Any
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from src.chart_builder import (
    add_category_sales_chart,
    add_daily_sales_chart,
    add_sales_rep_chart,
)

# Colors and Styling constants
HEADER_FILL = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")  # Navy Blue
HEADER_FONT = Font(name="游ゴシック", size=11, bold=True, color="FFFFFF")

ERROR_HEADER_FILL = PatternFill(start_color="8B0000", end_color="8B0000", fill_type="solid")  # Dark Red
ERROR_HEADER_FONT = Font(name="游ゴシック", size=11, bold=True, color="FFFFFF")

KPI_TITLE_FILL = PatternFill(start_color="E6EEF8", end_color="E6EEF8", fill_type="solid")
KPI_TITLE_FONT = Font(name="游ゴシック", size=10, bold=True, color="1B365D")
KPI_VALUE_FONT = Font(name="游ゴシック", size=16, bold=True, color="000000")

REGULAR_FONT = Font(name="游ゴシック", size=10)
TOTAL_ROW_FONT = Font(name="游ゴシック", size=10, bold=True)
TOTAL_ROW_FILL = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")

THIN_BORDER = Border(
    left=Side(style="thin", color="D3D3D3"),
    right=Side(style="thin", color="D3D3D3"),
    top=Side(style="thin", color="D3D3D3"),
    bottom=Side(style="thin", color="D3D3D3"),
)


def _apply_header_style(ws, headers: list, is_error: bool = False) -> None:
    """Apply styling to the header row."""
    fill = ERROR_HEADER_FILL if is_error else HEADER_FILL
    font = ERROR_HEADER_FONT if is_error else HEADER_FONT

    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.fill = fill
        cell.font = font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER
    ws.row_dimensions[1].height = 28


def _auto_fit_columns(ws, max_col: int) -> None:
    """Adjust column widths dynamically based on content length."""
    for col_idx in range(1, max_col + 1):
        col_letter = get_column_letter(col_idx)
        max_len = 0
        for row in range(1, ws.max_row + 1):
            val = ws.cell(row=row, column=col_idx).value
            if val is not None:
                # Japanese text width handling approx 1.8x
                s_val = str(val)
                length = sum(2 if ord(c) > 127 else 1 for c in s_val)
                if length > max_len:
                    max_len = length
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)


def generate_excel_report(
    summary_data: Dict[str, Any],
    daily_df,
    rep_df,
    cat_df,
    product_df,
    error_df,
    output_path: str | Path,
) -> Path:
    """
    Generate complete Excel business report workbook with multi-sheets and charts.

    Args:
        summary_data (Dict[str, Any]): High-level summary metrics.
        daily_df (pd.DataFrame): Daily sales aggregation.
        rep_df (pd.DataFrame): Sales rep aggregation.
        cat_df (pd.DataFrame): Category aggregation.
        product_df (pd.DataFrame): Product aggregation.
        error_df (pd.DataFrame): Error data records.
        output_path (str | Path): Destination file path.

    Returns:
        Path: Output file path.
    """
    out_file = Path(output_path)
    if out_file.is_dir():
        out_file = out_file / "業務売上レポート.xlsx"

    # Ensure parent directory exists
    out_file.parent.mkdir(parents=True, exist_ok=True)

    wb = openpyxl.Workbook()

    # 1. Summary Sheet (サマリー)
    ws_summary = wb.active
    ws_summary.title = "サマリー"
    ws_summary.views.sheetView[0].showGridLines = True

    # Title
    ws_summary["A1"] = "業務売上集計サマリーレポート"
    ws_summary["A1"].font = Font(name="游ゴシック", size=16, bold=True, color="1B365D")
    ws_summary.row_dimensions[1].height = 32

    # KPI Block setup
    kpi_items = [
        ("総売上", summary_data["total_sales"], "¥#,##0", "B3", "B4"),
        ("総販売数量", summary_data["total_quantity"], "#,##0個", "D3", "D4"),
        ("注文件数", summary_data["order_count"], "#,##0件", "F3", "F4"),
        ("平均注文金額", summary_data["avg_order_amount"], "¥#,##0", "H3", "H4"),
    ]

    for title, val, num_fmt, t_cell, v_cell in kpi_items:
        ws_summary[t_cell] = title
        ws_summary[t_cell].fill = KPI_TITLE_FILL
        ws_summary[t_cell].font = KPI_TITLE_FONT
        ws_summary[t_cell].alignment = Alignment(horizontal="center", vertical="center")
        ws_summary[t_cell].border = THIN_BORDER

        ws_summary[v_cell] = val
        ws_summary[v_cell].font = KPI_VALUE_FONT
        ws_summary[v_cell].alignment = Alignment(horizontal="center", vertical="center")
        ws_summary[v_cell].border = THIN_BORDER

        if "¥" in num_fmt:
            ws_summary[v_cell].number_format = "¥#,##0"
        elif "件" in num_fmt:
            ws_summary[v_cell].number_format = '#,##0"件"'
        elif "個" in num_fmt:
            ws_summary[v_cell].number_format = '#,##0"個"'

    ws_summary.row_dimensions[3].height = 20
    ws_summary.row_dimensions[4].height = 28

    # Summary Tables - Rep Sales TOP
    ws_summary["A7"] = "【担当者別売上】"
    ws_summary["A7"].font = Font(name="游ゴシック", size=12, bold=True, color="1B365D")

    rep_headers = ["担当者", "売上金額", "数量", "売上構成比(%)"]
    for c_idx, h in enumerate(rep_headers, 1):
        cell = ws_summary.cell(row=8, column=c_idx, value=h)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center")

    r_row = 9
    for _, row in rep_df.iterrows():
        ws_summary.cell(row=r_row, column=1, value=row["担当者"]).alignment = Alignment(horizontal="left")
        c_amt = ws_summary.cell(row=r_row, column=2, value=row["売上金額"])
        c_amt.number_format = "¥#,##0"
        c_qty = ws_summary.cell(row=r_row, column=3, value=row["数量"])
        c_qty.number_format = "#,##0"
        c_ratio = ws_summary.cell(row=r_row, column=4, value=row["売上構成比(%)"] / 100)
        c_ratio.number_format = "0.0%"

        for col_i in range(1, 5):
            ws_summary.cell(row=r_row, column=col_i).border = THIN_BORDER
            ws_summary.cell(row=r_row, column=col_i).font = REGULAR_FONT
        r_row += 1

    # Summary Tables - Category Sales TOP
    ws_summary["F7"] = "【カテゴリ別売上】"
    ws_summary["F7"].font = Font(name="游ゴシック", size=12, bold=True, color="1B365D")

    cat_headers = ["商品カテゴリ", "売上金額", "数量", "売上構成比(%)"]
    for c_idx, h in enumerate(cat_headers, 6):
        cell = ws_summary.cell(row=8, column=c_idx, value=h)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center")

    c_row = 9
    for _, row in cat_df.iterrows():
        ws_summary.cell(row=c_row, column=6, value=row["商品カテゴリ"]).alignment = Alignment(horizontal="left")
        c_amt = ws_summary.cell(row=c_row, column=7, value=row["売上金額"])
        c_amt.number_format = "¥#,##0"
        c_qty = ws_summary.cell(row=c_row, column=8, value=row["数量"])
        c_qty.number_format = "#,##0"
        c_ratio = ws_summary.cell(row=c_row, column=9, value=row["売上構成比(%)"] / 100)
        c_ratio.number_format = "0.0%"

        for col_i in range(6, 10):
            ws_summary.cell(row=c_row, column=col_i).border = THIN_BORDER
            ws_summary.cell(row=c_row, column=col_i).font = REGULAR_FONT
        c_row += 1

    _auto_fit_columns(ws_summary, 10)

    # 2. Daily Aggregation Sheet (日別集計)
    ws_daily = wb.create_sheet(title="日別集計")
    ws_daily.views.sheetView[0].showGridLines = True
    daily_headers = ["注文日", "売上金額", "注文件数"]
    _apply_header_style(ws_daily, daily_headers)

    d_row = 2
    for _, row in daily_df.iterrows():
        ws_daily.cell(row=d_row, column=1, value=row["注文日"]).alignment = Alignment(horizontal="center")
        c_amt = ws_daily.cell(row=d_row, column=2, value=row["売上金額"])
        c_amt.number_format = "¥#,##0"
        c_cnt = ws_daily.cell(row=d_row, column=3, value=row["注文件数"])
        c_cnt.number_format = "#,##0"

        for col_i in range(1, 4):
            ws_daily.cell(row=d_row, column=col_i).border = THIN_BORDER
            ws_daily.cell(row=d_row, column=col_i).font = REGULAR_FONT
        d_row += 1

    _auto_fit_columns(ws_daily, 3)
    add_daily_sales_chart(ws_daily, max_row=d_row - 1, cell_target="E2")

    # 3. Sales Rep Sheet (担当者別集計)
    ws_rep = wb.create_sheet(title="担当者別集計")
    ws_rep.views.sheetView[0].showGridLines = True
    _apply_header_style(ws_rep, rep_headers)

    rep_r = 2
    for _, row in rep_df.iterrows():
        ws_rep.cell(row=rep_r, column=1, value=row["担当者"]).alignment = Alignment(horizontal="left")
        c_amt = ws_rep.cell(row=rep_r, column=2, value=row["売上金額"])
        c_amt.number_format = "¥#,##0"
        c_qty = ws_rep.cell(row=rep_r, column=3, value=row["数量"])
        c_qty.number_format = "#,##0"
        c_ratio = ws_rep.cell(row=rep_r, column=4, value=row["売上構成比(%)"] / 100)
        c_ratio.number_format = "0.0%"

        for col_i in range(1, 5):
            ws_rep.cell(row=rep_r, column=col_i).border = THIN_BORDER
            ws_rep.cell(row=rep_r, column=col_i).font = REGULAR_FONT
        rep_r += 1

    _auto_fit_columns(ws_rep, 4)
    add_sales_rep_chart(ws_rep, max_row=rep_r - 1, cell_target="F2")

    # 4. Category Sheet (カテゴリ別集計)
    ws_cat = wb.create_sheet(title="カテゴリ別集計")
    ws_cat.views.sheetView[0].showGridLines = True
    _apply_header_style(ws_cat, cat_headers)

    cat_r = 2
    for _, row in cat_df.iterrows():
        ws_cat.cell(row=cat_r, column=1, value=row["商品カテゴリ"]).alignment = Alignment(horizontal="left")
        c_amt = ws_cat.cell(row=cat_r, column=2, value=row["売上金額"])
        c_amt.number_format = "¥#,##0"
        c_qty = ws_cat.cell(row=cat_r, column=3, value=row["数量"])
        c_qty.number_format = "#,##0"
        c_ratio = ws_cat.cell(row=cat_r, column=4, value=row["売上構成比(%)"] / 100)
        c_ratio.number_format = "0.0%"

        for col_i in range(1, 5):
            ws_cat.cell(row=cat_r, column=col_i).border = THIN_BORDER
            ws_cat.cell(row=cat_r, column=col_i).font = REGULAR_FONT
        cat_r += 1

    _auto_fit_columns(ws_cat, 4)
    add_category_sales_chart(ws_cat, max_row=cat_r - 1, cell_target="F2")

    # 5. Product Sheet (商品別集計)
    ws_prod = wb.create_sheet(title="商品別集計")
    ws_prod.views.sheetView[0].showGridLines = True
    prod_headers = ["商品名", "商品カテゴリ", "売上金額", "数量"]
    _apply_header_style(ws_prod, prod_headers)

    p_row = 2
    for _, row in product_df.iterrows():
        ws_prod.cell(row=p_row, column=1, value=row["商品名"]).alignment = Alignment(horizontal="left")
        ws_prod.cell(row=p_row, column=2, value=row["商品カテゴリ"]).alignment = Alignment(horizontal="left")
        c_amt = ws_prod.cell(row=p_row, column=3, value=row["売上金額"])
        c_amt.number_format = "¥#,##0"
        c_qty = ws_prod.cell(row=p_row, column=4, value=row["数量"])
        c_qty.number_format = "#,##0"

        for col_i in range(1, 5):
            ws_prod.cell(row=p_row, column=col_i).border = THIN_BORDER
            ws_prod.cell(row=p_row, column=col_i).font = REGULAR_FONT
        p_row += 1

    _auto_fit_columns(ws_prod, 4)

    # 6. Error Data Sheet (エラーデータ)
    ws_err = wb.create_sheet(title="エラーデータ")
    ws_err.views.sheetView[0].showGridLines = True
    err_headers = ["元行番号", "注文日", "注文番号", "商品カテゴリ", "商品名", "数量", "売上金額", "担当者", "エラー理由"]
    _apply_header_style(ws_err, err_headers, is_error=True)

    e_row = 2
    if not error_df.empty:
        for _, row in error_df.iterrows():
            for c_idx, h_col in enumerate(err_headers, 1):
                val = row.get(h_col, "")
                cell = ws_err.cell(row=e_row, column=c_idx, value=val)
                cell.font = REGULAR_FONT
                cell.border = THIN_BORDER
                if h_col in ["元行番号", "注文日"]:
                    cell.alignment = Alignment(horizontal="center")
            e_row += 1
    _auto_fit_columns(ws_err, len(err_headers))

    # Save Excel file
    try:
        wb.save(out_file)
    except PermissionError:
        raise PermissionError(
            f"Excelファイルの保存に失敗しました: {out_file.name}\n"
            f"【原因】同名のExcelファイルが開かれている可能性があります。\n"
            f"【対処方法】開いているExcelファイルを閉じてから再度実行してください。"
        )
    except Exception as e:
        raise IOError(
            f"Excelファイルの保存中にエラーが発生しました: {e}\n"
            f"【対処方法】保存先フォルダへのアクセス権限や空き容量を確認してください。"
        )

    return out_file
