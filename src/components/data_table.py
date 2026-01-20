"""データテーブルコンポーネント"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
import pandas as pd


class DataTable(ttk.Frame):
    """データテーブル表示"""

    def __init__(
        self,
        parent,
        columns: list[dict],
        searchable: bool = True,
        **kwargs
    ):
        """初期化

        Args:
            parent: 親ウィジェット
            columns: カラム定義のリスト [{'text': '列名', 'stretch': True}, ...]
            searchable: 検索機能を有効にするか
        """
        super().__init__(parent, **kwargs)

        self.columns = columns
        self.searchable = searchable
        self._data = []

        self._create_widgets()

    def _create_widgets(self):
        """ウィジェットを作成"""
        # 検索バー
        if self.searchable:
            search_frame = ttk.Frame(self)
            search_frame.pack(fill=X, pady=(0, 5))

            ttk.Label(search_frame, text="検索:").pack(side=LEFT, padx=(0, 5))
            self.search_var = ttk.StringVar()
            self.search_entry = ttk.Entry(
                search_frame,
                textvariable=self.search_var,
                width=30
            )
            self.search_entry.pack(side=LEFT, fill=X, expand=True)
            self.search_var.trace_add('write', self._on_search)

        # テーブル
        col_data = [col['text'] for col in self.columns]
        self.table = Tableview(
            self,
            coldata=col_data,
            rowdata=[],
            paginated=True,
            pagesize=20,
            searchable=False,  # 独自の検索を使用
            bootstyle=PRIMARY,
            stripecolor=('#f8f9fa', None)
        )
        self.table.pack(fill=BOTH, expand=True)

    def _on_search(self, *args):
        """検索時のコールバック"""
        search_text = self.search_var.get().lower()
        if not search_text:
            self.table.load_table_data(self._data)
            return

        filtered = [
            row for row in self._data
            if any(search_text in str(cell).lower() for cell in row)
        ]
        self.table.load_table_data(filtered)

    def load_dataframe(self, df: pd.DataFrame):
        """DataFrameからデータを読み込み

        Args:
            df: 表示するDataFrame
        """
        # カラム名を取得
        col_names = [col['text'] for col in self.columns]

        # DataFrameから該当カラムのデータを抽出
        display_cols = [c for c in col_names if c in df.columns]

        if not display_cols:
            self._data = []
            self.table.load_table_data([])
            return

        # データを行リストに変換
        self._data = df[display_cols].values.tolist()

        # 数値のフォーマット
        for row in self._data:
            for i, val in enumerate(row):
                if isinstance(val, (int, float)):
                    row[i] = f"{val:,.0f}"

        self.table.load_table_data(self._data)

    def load_data(self, data: list[list]):
        """リストデータを読み込み

        Args:
            data: 行データのリスト
        """
        self._data = data
        self.table.load_table_data(self._data)

    def clear(self):
        """データをクリア"""
        self._data = []
        self.table.load_table_data([])


class SummaryTable(ttk.Frame):
    """サマリーテーブル（シンプルな2列表示）"""

    def __init__(self, parent, title: str = "", **kwargs):
        super().__init__(parent, **kwargs)

        self.title = title
        self.rows = []

        self._create_widgets()

    def _create_widgets(self):
        """ウィジェットを作成"""
        if self.title:
            ttk.Label(
                self,
                text=self.title,
                font=("", 11, "bold")
            ).pack(anchor=W, pady=(0, 10))

        self.table_frame = ttk.Frame(self)
        self.table_frame.pack(fill=BOTH, expand=True)

    def add_row(
        self,
        label: str,
        value: str,
        is_header: bool = False,
        highlight: bool = False
    ):
        """行を追加

        Args:
            label: ラベル
            value: 値
            is_header: ヘッダー行か
            highlight: ハイライトするか
        """
        row_frame = ttk.Frame(self.table_frame)
        row_frame.pack(fill=X, pady=1)

        font = ("", 10, "bold") if is_header or highlight else ("", 10)
        fg = "primary" if highlight else None

        label_widget = ttk.Label(
            row_frame,
            text=label,
            font=font,
            width=20,
            anchor=W
        )
        label_widget.pack(side=LEFT, padx=(0, 10))

        value_widget = ttk.Label(
            row_frame,
            text=value,
            font=font,
            anchor=E
        )
        value_widget.pack(side=RIGHT)

        self.rows.append((label_widget, value_widget))

    def clear(self):
        """行をクリア"""
        for label_w, value_w in self.rows:
            label_w.destroy()
            value_w.destroy()
        self.rows = []

    def update_rows(self, data: list[tuple[str, str, bool, bool]]):
        """行を更新

        Args:
            data: [(ラベル, 値, is_header, highlight), ...] のリスト
        """
        self.clear()
        for item in data:
            if len(item) == 2:
                label, value = item
                self.add_row(label, value)
            elif len(item) == 3:
                label, value, is_header = item
                self.add_row(label, value, is_header)
            else:
                label, value, is_header, highlight = item
                self.add_row(label, value, is_header, highlight)
