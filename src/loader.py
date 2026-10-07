"""
CSV loading module with auto-encoding detection and comprehensive error handling.
"""

from pathlib import Path
import pandas as pd


class CSVLoadError(Exception):
    """Custom exception raised when CSV loading fails."""
    pass


def load_csv(file_path: str | Path) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame with automatic encoding detection.

    Args:
        file_path (str | Path): Absolute or relative path to the CSV file.

    Returns:
        pd.DataFrame: Loaded raw sales DataFrame.

    Raises:
        CSVLoadError: If file is missing, empty, or unreadable.
    """
    path = Path(file_path)

    # 1. Existence check
    if not path.exists():
        raise CSVLoadError(
            f"指定されたファイルが見つかりません: {path}\n"
            f"【対処方法】ファイルパスが正しいか、ファイルが移動・削除されていないか確認してください。"
        )

    # 2. File type check
    if not path.is_file():
        raise CSVLoadError(
            f"指定されたパスはファイルではありません: {path}\n"
            f"【対処方法】フォルダではなく正しいCSVファイルを選択してください。"
        )

    # 3. Empty file check
    if path.stat().st_size == 0:
        raise CSVLoadError(
            f"ファイルが空です (0バイト): {path.name}\n"
            f"【対処方法】データが入っている正しいCSVファイルを選択してください。"
        )

    # 4. Try multiple encodings for robust Japanese text reading (UTF-8, UTF-8-SIG, Shift_JIS/CP932)
    encodings = ["utf-8-sig", "utf-8", "cp932"]
    df = None
    last_error = None

    for enc in encodings:
        try:
            df = pd.read_csv(path, encoding=enc)
            break
        except (UnicodeDecodeError, pd.errors.ParserError) as e:
            last_error = e
            continue

    if df is None:
        raise CSVLoadError(
            f"CSVファイルの読み込みに失敗しました: {path.name}\n"
            f"【詳細】文字コードの判定に失敗したか、ファイル形式が不正です ({last_error})\n"
            f"【対処方法】ファイルの文字コードを UTF-8 または Shift_JIS に保存し直してください。"
        )

    if df.empty:
        raise CSVLoadError(
            f"CSVファイルにデータ行が存在しません: {path.name}\n"
            f"【対処方法】ヘッダーだけでなくデータ行が含まれているか確認してください。"
        )

    return df
