# CSV業務レポート自動生成ツール (CSV Business Report Auto-Generator Tool)

![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Tests](https://img.shields.io/badge/Tests-11%20Passed-brightgreen.svg)

CSV形式の日常の売上業務データを読み込み、データバリデーション、売上集計、openpyxlによるスタイリッシュなExcelレポートおよびグラフ作成までをワンクリックで自動化するデスクトップアプリケーションです。

---

## 🌟 主な機能と特徴

1. **直感的な Tkinter GUI**
   - ファイルダイアログによる簡単CSV選択・出力先フォルダ選択。
   - バックグラウンドスレッド（threading）処理により、大きなデータ処理時もUIがフリーズしません。
   - リアルタイムな処理状況・ログ表示と、分かりやすい完了/エラーダイアログ。

2. **堅牢な文字コード対応 CSV ローダー (`loader.py`)**
   - UTF-8 (BOM付き含む) および Windows環境で一般的な Shift_JIS (CP932) の自動判定・読み込み。
   - ファイル非存在、空ファイル、フォルダ選択間違いに対する親切なエラー通知。

3. **高度なデータバリデーション & エラーデータ切り分け (`validator.py`)**
   - 必須列存在チェック (`注文日`, `注文番号`, `商品カテゴリ`, `商品名`, `数量`, `売上金額`, `担当者`)。
   - 日付形式、数値型、空欄データのチェック。
   - 正常データのみを集計し、不備のある異常データはExcelの「エラーデータ」シートへ元の行番号とエラー理由付きで自動出力。

4. **多角的なpandas売上集計 (`aggregator.py`)**
   - **サマリー指標**: 総売上、総販売数量、注文件数、平均注文金額
   - **担当者別集計**: 売上金額、数量、売上構成比(%)
   - **カテゴリ別集計**: 売上金額、数量、売上構成比(%)
   - **商品別集計**: 商品名・カテゴリ別の売上金額・数量
   - **日別集計**: 時系列の日別売上金額・注文件数

5. **openpyxlによる美しく装飾されたExcel & グラフ生成 (`excel_generator.py`, `chart_builder.py`)**
   - ビジネス仕様のカラーテーマ（ネイビー・ダークレッド）と数値フォーマット（¥#,##0, 構成比%）。
   - 折れ線グラフ（日別売上推移）および 棒グラフ（担当者別・カテゴリ別売上比較）の自動埋め込み。
   - 列幅の自動調整（Auto-fit）機能。

6. **pytest による高テストカバー率 (`tests/`)**
   - モジュールごとに独立した単体テストコードを完備（全11ケースパス確認済み）。

---

## 📁 プロジェクト構成

```
excel_tool_project/
├── data/
│   ├── sample_sales.csv         # 正常動作確認用サンプルCSV (40件)
│   └── sample_sales_invalid.csv # エラー検証用サンプルCSV (7件)
├── src/
│   ├── __init__.py
│   ├── loader.py                # CSVファイル読込・文字コード判定
│   ├── validator.py             # データバリデーション・エラー行分離
│   ├── aggregator.py            # pandasによる集計ロジック
│   ├── excel_generator.py       # openpyxl Excelシート作成・スタイリング
│   ├── chart_builder.py         # openpyxl グラフ作成・埋め込み
│   ├── reporter.py              # 全処理を統括するオーケストレーター
│   └── gui.py                   # Tkinter GUI画面
├── tests/
│   ├── __init__.py
│   ├── test_loader.py           # Loader単体テスト
│   ├── test_validator.py        # Validator単体テスト
│   ├── test_aggregator.py       # Aggregator単体テスト
│   └── test_excel_generator.py  # ExcelGenerator単体テスト
├── requirements.txt             # 依存ライブラリ一覧
├── main.py                      # アプリケーション起動エントリポイント
└── README.md                    # 本ドキュメント
```

---

## 🚀 セットアップと実行方法

### 1. 動作環境
- Python 3.10 以上
- Windows / macOS / Linux (Tkinter同梱環境)

### 2. 依存ライブラリのインストール
```bash
pip install -r requirements.txt
```

### 3. GUIアプリケーションの起動
```bash
python main.py
```
起動後、表示される画面から `data/sample_sales.csv` を選択し、「🚀 Excelレポートを作成する」ボタンをクリックしてください。

### 4. CLI（コマンドライン）モードでの実行
スクリプトやバッチ処理から直接実行する場合：
```bash
python main.py --cli data/sample_sales.csv output/
```

---

## 📊 生成されるExcelレポートの構成 (6シート)

| シート名 | 概要 |
| :--- | :--- |
| **サマリー** | 総売上・総数量・注文件数・平均注文額のKPIカード、担当者別・カテゴリ別売上TOPテーブル |
| **日別集計** | 注文日ごとの売上金額と注文件数テーブル ＋ **日別売上推移 折れ線グラフ** |
| **担当者別集計** | 担当者ごとの売上・数量・構成比 ＋ **担当者別売上 棒グラフ** |
| **カテゴリ別集計** | カテゴリごとの売上・数量・構成比 ＋ **カテゴリ別売上 棒グラフ** |
| **商品別集計** | 商品ごとの売上金額・数量一覧テーブル |
| **エラーデータ** | 不正データの元行番号、元のデータ、具体的なエラー理由の一覧 |

---

## 🧪 テストの実行

pytestを使用して全ての単体テストを実行できます。

```bash
pytest -v
```

### テスト項目一覧
- `test_load_valid_csv`: 正常CSVが読み込めるか
- `test_load_non_existent_csv`: 存在しないファイルで親切なエラーメッセージが出るか
- `test_load_empty_csv`: 0バイトファイルでエラー検知できるか
- `test_validate_missing_columns`: 必須列不足時に検出できるか
- `test_validate_separates_clean_and_error_rows`: 正常行とエラー行を正しく振り分けられるか
- `test_aggregate_summary`: KPI計算（平均・合計）の精度
- `test_aggregate_by_sales_rep`: 担当者別集計および構成比の正確さ
- `test_aggregate_by_category`: カテゴリ別集計の正確さ
- `test_aggregate_by_product`: 商品別集計の正確さ
- `test_aggregate_by_date`: 日別集計の昇順並び替え精度
- `test_generate_excel_report`: openpyxlで全6シートが正しく生成されるか

---

## 💡 設計と思想（Python学習者向け解説）

### 単一責任の原則 (Single Responsibility Principle)
各モジュールを `loader` (読込), `validator` (検査), `aggregator` (集計), `excel_generator` (描画), `gui` (UI) に完全に分離しています。これにより、例えばUIをWeb化したり、Excel出力をPDF出力に変更したい場合でも、他のモジュールを壊さずに修正が可能です。

### なぜ custom Exception を定義するのか？
`CSVLoadError` や `ValidationError` を独自定義することで、Python標準の技術的なトレースバック（`KeyError` や `ValueError` など）をそのままユーザーに見せるのではなく、「原因」と「具体的な対処方法」を含んだ親切なメッセージをGUI上に表示できます。

---

## 📜 ライセンス
MIT License
