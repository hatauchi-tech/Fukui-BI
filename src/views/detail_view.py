"""詳細データ画面"""
import os
from datetime import datetime
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from ..data_loader import DataLoader
from ..data_processor import DataProcessor
from ..components.data_table import DataTable


class DetailView(ttk.Frame):
    """詳細データ画面"""

    def __init__(
        self,
        parent,
        processor: DataProcessor,
        loader: DataLoader,
        **kwargs
    ):
        super().__init__(parent, **kwargs)

        self.processor = processor
        self.loader = loader
        self.current_df = None  # エクスポート用に保持

        self._create_widgets()
        self.refresh()

    def _create_widgets(self):
        """ウィジェットを作成"""
        # ヘッダー
        header = ttk.Frame(self)
        header.pack(fill=X, padx=20, pady=(20, 10))

        ttk.Label(
            header,
            text="詳細データ",
            font=("", 16, "bold")
        ).pack(side=LEFT)

        # フィルタセクション
        filter_section = ttk.LabelFrame(self, text="フィルタ")
        filter_section.pack(fill=X, padx=20, pady=10)

        filter_content = ttk.Frame(filter_section)
        filter_content.pack(fill=X, padx=10, pady=10)

        # 部門フィルタ
        ttk.Label(filter_content, text="部門:").pack(side=LEFT, padx=(0, 5))
        self.dept_var = ttk.StringVar(value="全部門")
        self.dept_combo = ttk.Combobox(
            filter_content,
            textvariable=self.dept_var,
            width=15,
            state="readonly"
        )
        self.dept_combo.pack(side=LEFT, padx=(0, 20))

        # 期間フィルタ
        ttk.Label(filter_content, text="期間:").pack(side=LEFT, padx=(0, 5))
        self.period_var = ttk.StringVar(value="全期間")
        self.period_combo = ttk.Combobox(
            filter_content,
            textvariable=self.period_var,
            width=12,
            state="readonly"
        )
        self.period_combo.pack(side=LEFT, padx=(0, 20))

        # 出力帳票フィルタ
        ttk.Label(filter_content, text="帳票:").pack(side=LEFT, padx=(0, 5))
        self.output_var = ttk.StringVar(value="損益計算書")
        self.output_combo = ttk.Combobox(
            filter_content,
            textvariable=self.output_var,
            width=15,
            state="readonly",
            values=["損益計算書", "製造原価内訳"]
        )
        self.output_combo.pack(side=LEFT, padx=(0, 20))

        # 適用ボタン
        ttk.Button(
            filter_content,
            text="適用",
            command=self._apply_filter,
            bootstyle="primary"
        ).pack(side=LEFT, padx=(0, 10))

        # CSVエクスポートボタン
        ttk.Button(
            filter_content,
            text="CSV出力",
            command=self._export_csv,
            bootstyle="outline-success"
        ).pack(side=RIGHT)

        # フィルタの初期値を設定
        self._update_filter_combos()

        # イベントバインド
        self.dept_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_filter())
        self.period_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_filter())
        self.output_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_filter())

        # データテーブル
        table_section = ttk.Frame(self)
        table_section.pack(fill=BOTH, expand=True, padx=20, pady=10)

        columns = [
            {'text': '部課名', 'stretch': True},
            {'text': '科目名', 'stretch': True},
            {'text': '前残高', 'stretch': False},
            {'text': '借方', 'stretch': False},
            {'text': '貸方', 'stretch': False},
            {'text': '残高', 'stretch': False},
        ]

        self.data_table = DataTable(table_section, columns=columns, searchable=True)
        self.data_table.pack(fill=BOTH, expand=True)

        # ステータスバー
        self.status_frame = ttk.Frame(self)
        self.status_frame.pack(fill=X, padx=20, pady=(0, 10))

        self.status_label = ttk.Label(
            self.status_frame,
            text="",
            bootstyle="secondary"
        )
        self.status_label.pack(side=LEFT)

    def _update_filter_combos(self):
        """フィルタコンボボックスを更新"""
        # 部門
        departments = self.loader.get_departments()
        dept_names = ["全部門"] + [name for _, name in departments]
        self.dept_combo["values"] = dept_names

        # 期間
        periods = self.loader.get_periods()
        period_values = ["全期間"] + periods
        self.period_combo["values"] = period_values

    def _get_selected_dept_code(self):
        """選択中の部門コードを取得"""
        selected = self.dept_var.get()
        if selected == "全部門":
            return None

        departments = self.loader.get_departments()
        for code, name in departments:
            if name == selected:
                return code
        return None

    def _get_selected_period(self):
        """選択中の期間を取得"""
        selected = self.period_var.get()
        return None if selected == "全期間" else selected

    def _get_selected_output_type(self):
        """選択中の出力帳票タイプを取得"""
        selected = self.output_var.get()
        return 0 if selected == "損益計算書" else 1

    def _apply_filter(self):
        """フィルタを適用"""
        self.refresh()

    def _export_csv(self):
        """CSVファイルとしてエクスポート"""
        if self.current_df is None or self.current_df.empty:
            messagebox.showwarning("警告", "エクスポートするデータがありません。")
            return

        # ファイル保存ダイアログ
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"詳細データ_{timestamp}.csv"

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSVファイル", "*.csv"), ("すべてのファイル", "*.*")],
            initialfile=default_filename,
            title="CSVファイルの保存"
        )

        if not filepath:
            return

        try:
            self.current_df.to_csv(filepath, index=False, encoding='utf-8-sig')
            messagebox.showinfo("完了", f"CSVファイルを保存しました:\n{filepath}")
        except Exception as e:
            messagebox.showerror("エラー", f"保存に失敗しました:\n{str(e)}")

    def refresh(self, year_month: str = None):
        """画面を更新

        Args:
            year_month: 対象年月（外部から指定された場合）
        """
        # 外部から期間が指定された場合はコンボボックスを更新
        if year_month is not None:
            if year_month in self.period_combo["values"]:
                self.period_var.set(year_month)
            else:
                self.period_var.set("全期間")

        # フィルタ条件を取得
        dept_code = self._get_selected_dept_code()
        period = self._get_selected_period()
        output_type = self._get_selected_output_type()

        # データを取得
        df = self.processor.get_detail_data(
            dept_code=dept_code,
            year_month=period,
            output_type=output_type
        )

        # 現在のデータを保持
        self.current_df = df.copy()

        # テーブルを更新
        self.data_table.load_dataframe(df)

        # ステータスを更新
        row_count = len(df)
        status_text = f"表示件数: {row_count:,}件"
        if dept_code is not None:
            status_text += f" | 部門: {self.dept_var.get()}"
        if period is not None:
            status_text += f" | 期間: {period}"

        self.status_label.configure(text=status_text)
