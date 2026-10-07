"""
Data validation module for sales CSV input.
Separates valid records from invalid error records and reports clear error details.
"""

from typing import Tuple
import pandas as pd


REQUIRED_COLUMNS = [
    "注文日",
    "注文番号",
    "商品カテゴリ",
    "商品名",
    "数量",
    "売上金額",
    "担当者",
]


class ValidationError(Exception):
    """Custom exception raised when required CSV schema is invalid."""
    pass


def validate_sales_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Validate sales DataFrame columns, data types, dates, and non-empty rules.

    Args:
        df (pd.DataFrame): Raw DataFrame read from CSV.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]:
            - clean_df: Validated DataFrame ready for aggregation.
            - error_df: Rejected records with '元行番号' and 'エラー理由'.

    Raises:
        ValidationError: If mandatory columns are missing from the input file.
    """
    # 1. Missing required column check
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        missing_str = "、".join(missing_cols)
        raise ValidationError(
            f"必須の列が不足しています: {missing_str}\n"
            f"【現在存在する列】: {', '.join(df.columns)}\n"
            f"【対処方法】CSVヘッダーに 『{missing_str}』 列を追加・修正してください。"
        )

    clean_rows = []
    error_rows = []

    # Iterate through each row and check business rules
    for idx, row in df.iterrows():
        row_num = idx + 2  # 1-indexed header + 1
        errors = []

        # Check required fields for blank/NaN values
        for col in REQUIRED_COLUMNS:
            val = row[col]
            if pd.isna(val) or str(val).strip() == "":
                errors.append(f"『{col}』が空欄です")

        # Quantity validation
        qty = None
        if not pd.isna(row["数量"]) and str(row["数量"]).strip() != "":
            try:
                qty = float(row["数量"])
                if qty < 0 or not qty.is_integer():
                    errors.append("『数量』は0以上の整数である必要があります")
                else:
                    qty = int(qty)
            except (ValueError, TypeError):
                errors.append(f"『数量』が数値ではありません ('{row['数量']}')")

        # Sales amount validation
        amount = None
        if not pd.isna(row["売上金額"]) and str(row["売上金額"]).strip() != "":
            try:
                amount = float(row["売上金額"])
                if amount < 0:
                    errors.append("『売上金額』は0以上である必要があります")
            except (ValueError, TypeError):
                errors.append(f"『売上金額』が数値ではありません ('{row['売上金額']}')")

        # Date format validation
        formatted_date = None
        if not pd.isna(row["注文日"]) and str(row["注文日"]).strip() != "":
            try:
                dt = pd.to_datetime(row["注文日"])
                formatted_date = dt.strftime("%Y-%m-%d")
            except Exception:
                errors.append(f"『注文日』の日付形式が不正です ('{row['注文日']}')")

        # Categorize row as clean or error
        if errors:
            err_dict = row.to_dict()
            err_dict["元行番号"] = row_num
            err_dict["エラー理由"] = " / ".join(errors)
            error_rows.append(err_dict)
        else:
            clean_dict = row.to_dict()
            clean_dict["注文日"] = formatted_date
            clean_dict["数量"] = qty
            clean_dict["売上金額"] = amount
            clean_rows.append(clean_dict)

    clean_df = pd.DataFrame(clean_rows)
    if clean_df.empty:
        clean_df = pd.DataFrame(columns=REQUIRED_COLUMNS)
    else:
        clean_df = clean_df[REQUIRED_COLUMNS]

    error_cols = ["元行番号"] + REQUIRED_COLUMNS + ["エラー理由"]
    error_df = pd.DataFrame(error_rows)
    if error_df.empty:
        error_df = pd.DataFrame(columns=error_cols)
    else:
        error_df = error_df[error_cols]

    return clean_df, error_df
