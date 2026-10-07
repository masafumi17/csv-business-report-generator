"""
CSV Business Report Auto-Generator Tool
Application Entry Point. Supports GUI launch by default or CLI processing.
"""

import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from src.gui import launch_gui
from src.reporter import generate_report


def main():
    """Entry point for the application."""
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        print("=== CSV業務レポート自動生成ツール (CLIモード) ===")
        csv_file = sys.argv[2] if len(sys.argv) > 2 else "data/sample_sales.csv"
        out_dir = sys.argv[3] if len(sys.argv) > 3 else "output"

        try:
            saved_file = generate_report(csv_file, out_dir, log_callback=print)
            print(f"\n[成功] レポートを生成しました: {saved_file.resolve()}")
        except Exception as e:
            print(f"\n[エラー] 処理に失敗しました: {e}")
            sys.exit(1)
    else:
        # Launch Tkinter GUI
        launch_gui()


if __name__ == "__main__":
    main()
