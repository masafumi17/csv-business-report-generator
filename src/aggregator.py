"""
Data aggregation module using pandas.
Calculates summary KPIs and multi-dimensional aggregations (sales rep, category, product, daily).
"""

from typing import Dict, Any
import pandas as pd


def aggregate_summary(clean_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate high-level summary KPIs from valid sales data.

    Args:
        clean_df (pd.DataFrame): Validated clean sales DataFrame.

    Returns:
        Dict[str, Any]: Summary dictionary containing total sales, total qty, order count, avg order value.
    """
    if clean_df.empty:
        return {
            "total_sales": 0,
            "total_quantity": 0,
            "order_count": 0,
            "avg_order_amount": 0.0,
        }

    total_sales = float(clean_df["売上金額"].sum())
    total_quantity = int(clean_df["数量"].sum())
    # Count unique order IDs if present, otherwise row count
    unique_orders = clean_df["注文番号"].nunique()
    order_count = int(unique_orders) if unique_orders > 0 else len(clean_df)
    avg_order_amount = float(total_sales / order_count) if order_count > 0 else 0.0

    return {
        "total_sales": total_sales,
        "total_quantity": total_quantity,
        "order_count": order_count,
        "avg_order_amount": round(avg_order_amount, 2),
    }


def aggregate_by_sales_rep(clean_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate total sales amount and quantity by sales representative.

    Args:
        clean_df (pd.DataFrame): Validated clean sales DataFrame.

    Returns:
        pd.DataFrame: Grouped DataFrame sorted by sales amount descending.
    """
    if clean_df.empty:
        return pd.DataFrame(columns=["担当者", "売上金額", "数量", "売上構成比(%)"])

    grouped = (
        clean_df.groupby("担当者", as_index=False)
        .agg({"売上金額": "sum", "数量": "sum"})
        .sort_values(by="売上金額", ascending=False)
    )

    total_sales = grouped["売上金額"].sum()
    grouped["売上構成比(%)"] = (
        (grouped["売上金額"] / total_sales * 100).round(1) if total_sales > 0 else 0.0
    )
    return grouped


def aggregate_by_category(clean_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate total sales amount and quantity by product category.

    Args:
        clean_df (pd.DataFrame): Validated clean sales DataFrame.

    Returns:
        pd.DataFrame: Grouped DataFrame sorted by sales amount descending.
    """
    if clean_df.empty:
        return pd.DataFrame(columns=["商品カテゴリ", "売上金額", "数量", "売上構成比(%)"])

    grouped = (
        clean_df.groupby("商品カテゴリ", as_index=False)
        .agg({"売上金額": "sum", "数量": "sum"})
        .sort_values(by="売上金額", ascending=False)
    )

    total_sales = grouped["売上金額"].sum()
    grouped["売上構成比(%)"] = (
        (grouped["売上金額"] / total_sales * 100).round(1) if total_sales > 0 else 0.0
    )
    return grouped


def aggregate_by_product(clean_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate total sales amount and quantity by product name.

    Args:
        clean_df (pd.DataFrame): Validated clean sales DataFrame.

    Returns:
        pd.DataFrame: Grouped DataFrame sorted by sales amount descending.
    """
    if clean_df.empty:
        return pd.DataFrame(columns=["商品名", "商品カテゴリ", "売上金額", "数量"])

    grouped = (
        clean_df.groupby(["商品名", "商品カテゴリ"], as_index=False)
        .agg({"売上金額": "sum", "数量": "sum"})
        .sort_values(by="売上金額", ascending=False)
    )
    return grouped[["商品名", "商品カテゴリ", "売上金額", "数量"]]


def aggregate_by_date(clean_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate total sales amount and order count by order date.

    Args:
        clean_df (pd.DataFrame): Validated clean sales DataFrame.

    Returns:
        pd.DataFrame: Grouped DataFrame sorted chronologically by order date.
    """
    if clean_df.empty:
        return pd.DataFrame(columns=["注文日", "売上金額", "注文件数"])

    grouped = (
        clean_df.groupby("注文日", as_index=False)
        .agg({"売上金額": "sum", "注文番号": "nunique"})
        .rename(columns={"注文番号": "注文件数"})
        .sort_values(by="注文日", ascending=True)
    )
    return grouped
