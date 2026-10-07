"""
Desktop Graphical User Interface (GUI) module built with Tkinter.
Provides non-technical users with intuitive file picking, output folder selection,
real-time progress updates, and friendly error dialogs.
"""

from pathlib import Path
import threading
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from src.reporter import generate_report


class Application(tk.Tk):
    """Main Tkinter GUI Application window for CSV Business Report Generator."""

    def __init__(self):
        super().__init__()
        self.title("CSV業務レポート自動生成ツール")
        self.geometry("700x560")
        self.minsize(620, 500)

        # Style configuration
        self._setup_styles()

        # State variables
        self.csv_path_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.is_processing = False

        # Build UI layout
        self._create_widgets()

    def _setup_styles(self):
        """Configure ttk custom styles."""
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Fonts
        default_font = ("Yu Gothic UI", 10)
        header_font = ("Yu Gothic UI", 14, "bold")
        btn_font = ("Yu Gothic UI", 10, "bold")

        self.option_add("*Font", default_font)

        # Color definitions
        NAVY = "#1B365D"
        BG_LIGHT = "#F8F9FA"

        self.configure(bg=BG_LIGHT)
        self.style.configure(".", background=BG_LIGHT, font=default_font)

        self.style.configure("Header.TLabel", font=header_font, foreground=NAVY, background=BG_LIGHT)
        self.style.configure("SubHeader.TLabel", font=default_font, foreground="#555555", background=BG_LIGHT)
        self.style.configure("TLabelframe", background=BG_LIGHT)
        self.style.configure("TLabelframe.Label", font=("Yu Gothic UI", 10, "bold"), foreground=NAVY, background=BG_LIGHT)

        # Action Button Style
        self.style.configure(
            "Primary.TButton",
            font=("Yu Gothic UI", 11, "bold"),
            background=NAVY,
            foreground="#FFFFFF",
            padding=(20, 8),
        )
        self.style.map(
            "Primary.TButton",
            background=[("active", "#2C4D75"), ("disabled", "#CCCCCC")],
            foreground=[("disabled", "#888888")],
        )

    def _create_widgets(self):
        """Construct all GUI frames, buttons, labels, and text widgets."""
        main_frame = ttk.Frame(self, padding="20 15 20 15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Header Title
        title_label = ttk.Label(main_frame, text="📊 CSV業務レポート自動生成ツール", style="Header.TLabel")
        title_label.pack(anchor=tk.W, pady=(0, 2))

        desc_label = ttk.Label(
            main_frame,
            text="売上CSVデータを選択し、ワンクリックで多機能Excelレポートを作成します。",
            style="SubHeader.TLabel",
        )
        desc_label.pack(anchor=tk.W, pady=(0, 15))

        # 2. File Selection Frame
        file_frame = ttk.LabelFrame(main_frame, text=" ファイル設定 ", padding="15 10 15 15")
        file_frame.pack(fill=tk.X, pady=(0, 15))

        # CSV File Row
        ttk.Label(file_frame, text="入力CSVファイル:").grid(row=0, column=0, sticky=tk.W, pady=5)
        csv_entry = ttk.Entry(file_frame, textvariable=self.csv_path_var, width=50)
        csv_entry.grid(row=0, column=1, padx=(10, 10), pady=5, sticky=tk.EW)
        btn_csv = ttk.Button(file_frame, text="参照...", command=self._browse_csv)
        btn_csv.grid(row=0, column=2, pady=5)

        # Output Folder Row
        ttk.Label(file_frame, text="出力先フォルダ:").grid(row=1, column=0, sticky=tk.W, pady=5)
        out_entry = ttk.Entry(file_frame, textvariable=self.output_dir_var, width=50)
        out_entry.grid(row=1, column=1, padx=(10, 10), pady=5, sticky=tk.EW)
        btn_out = ttk.Button(file_frame, text="参照...", command=self._browse_output_dir)
        btn_out.grid(row=1, column=2, pady=5)

        file_frame.columnconfigure(1, weight=1)

        # 3. Action Section
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(0, 15))

        self.btn_run = ttk.Button(
            action_frame,
            text="🚀 Excelレポートを作成する",
            style="Primary.TButton",
            command=self._start_processing,
        )
        self.btn_run.pack(pady=5)

        # Progress bar
        self.progress_bar = ttk.Progressbar(action_frame, mode="indeterminate")
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))

        # 4. Status & Log Output Frame
        log_frame = ttk.LabelFrame(main_frame, text=" 処理状況・ログ ", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = ScrolledText(
            log_frame,
            wrap=tk.WORD,
            height=10,
            font=("Consolas", 9),
            bg="#1E1E1E",
            fg="#D4D4D4",
            insertbackground="white",
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Pre-fill sample CSV path if available
        sample_path = Path.cwd() / "data" / "sample_sales.csv"
        if sample_path.exists():
            self.csv_path_var.set(str(sample_path.resolve()))

        default_out = Path.cwd() / "output"
        self.output_dir_var.set(str(default_out.resolve()))

        self._log_message("システム準備完了。CSVファイルと出力先フォルダを指定してください。\n")

    def _browse_csv(self):
        """Open file dialog to choose CSV file."""
        selected = filedialog.askopenfilename(
            title="入力CSVファイルを選択",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        )
        if selected:
            self.csv_path_var.set(selected)
            # Auto set output dir to same directory if not specified
            if not self.output_dir_var.get():
                self.output_dir_var.set(str(Path(selected).parent.resolve()))

    def _browse_output_dir(self):
        """Open directory dialog to choose output folder."""
        selected = filedialog.askdirectory(title="出力先フォルダを選択")
        if selected:
            self.output_dir_var.set(selected)

    def _log_message(self, message: str):
        """Append message string to the GUI log text box."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _start_processing(self):
        """Validate GUI inputs and launch background worker thread."""
        csv_file = self.csv_path_var.get().strip()
        output_dir = self.output_dir_var.get().strip()

        if not csv_file:
            messagebox.showwarning(
                "入力エラー",
                "CSVファイルが指定されていません。\n「参照...」ボタンよりCSVファイルを選択してください。",
            )
            return

        if not output_dir:
            messagebox.showwarning(
                "入力エラー",
                "出力先フォルダが指定されていません。\n「参照...」ボタンよりフォルダを選択してください。",
            )
            return

        # Disable button & start progress bar
        self.is_processing = True
        self.btn_run.config(state=tk.DISABLED)
        self.progress_bar.start(10)
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

        self._log_message(f"=== 処理開始 [{Path(csv_file).name}] ===")

        # Run background thread to keep UI responsive
        threading.Thread(
            target=self._run_report_worker,
            args=(csv_file, output_dir),
            daemon=True,
        ).start()

    def _run_report_worker(self, csv_file: str, output_dir: str):
        """Worker thread executing report generation logic."""
        try:
            saved_path = generate_report(
                csv_path=csv_file,
                output_dir=output_dir,
                log_callback=self._log_message,
            )

            # UI Update on main thread
            self.after(0, lambda: self._on_success(saved_path))

        except Exception as err:
            err_msg = str(err)
            self.after(0, lambda: self._on_error(err_msg))

    def _on_success(self, saved_path: Path):
        """Handle processing completion."""
        self.progress_bar.stop()
        self.btn_run.config(state=tk.NORMAL)
        self.is_processing = False

        self._log_message("\n🎉 レポート生成が正常に完了しました！")
        self._log_message(f"保存場所: {saved_path.resolve()}")

        messagebox.showinfo(
            "処理完了",
            f"Excelレポートの作成が完了しました！\n\n"
            f"【出力ファイル】\n{saved_path.name}\n\n"
            f"【保存場所】\n{saved_path.parent.resolve()}",
        )

    def _on_error(self, error_message: str):
        """Handle processing errors gracefully."""
        self.progress_bar.stop()
        self.btn_run.config(state=tk.NORMAL)
        self.is_processing = False

        self._log_message(f"\n❌ エラーが発生しました:\n{error_message}")

        messagebox.showerror(
            "処理エラー",
            f"レポート作成中にエラーが発生しました。\n\n{error_message}",
        )


def launch_gui():
    """Launch the main Tkinter desktop GUI application."""
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    launch_gui()
