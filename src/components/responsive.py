"""レスポンシブレイアウトコンポーネント"""
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from .theme import Colors, Spacing


class ResponsiveRow(ttk.Frame):
    """幅に応じて横並び/縦並びを切り替えるコンテナ

    幅が閾値以上なら子要素を横並び、それ以下なら縦並びにする
    """

    def __init__(self, parent, breakpoint: int = 800, **kwargs):
        """
        Args:
            parent: 親ウィジェット
            breakpoint: 横並びに切り替わる幅の閾値（ピクセル）
        """
        super().__init__(parent, **kwargs)

        self.breakpoint = breakpoint
        self._children = []
        self._is_horizontal = True
        self._resize_job = None
        self._last_width = None

        self.bind('<Configure>', self._on_resize)

    def add_child(self, widget, weight: int = 1, min_width: int = 200):
        """子ウィジェットを追加

        Args:
            widget: 追加するウィジェット
            weight: 横並び時の幅の比率
            min_width: 最小幅（ピクセル）
        """
        self._children.append({
            'widget': widget,
            'weight': weight,
            'min_width': min_width
        })

        # 初期配置（横並び）
        widget.pack(side=LEFT, fill=BOTH, expand=True, padx=Spacing.SM)

    def _on_resize(self, event):
        """リサイズイベント処理"""
        if event.width < 100:
            return

        if self._last_width == event.width:
            return

        self._last_width = event.width

        # 既存のジョブをキャンセル
        if self._resize_job:
            self.after_cancel(self._resize_job)

        # 100ms後に再配置（デバウンス）
        self._resize_job = self.after(100, lambda: self._relayout(event.width))

    def _relayout(self, width: int):
        """レイアウトを再構築"""
        should_be_horizontal = width >= self.breakpoint

        # 変更がなければスキップ
        if should_be_horizontal == self._is_horizontal and self._children:
            # 既に配置済みならスキップ
            return

        self._is_horizontal = should_be_horizontal

        # 全ての子ウィジェットのpackを解除
        for child_info in self._children:
            child_info['widget'].pack_forget()

        # 再配置
        if should_be_horizontal:
            # 横並び
            for child_info in self._children:
                child_info['widget'].pack(
                    side=LEFT,
                    fill=BOTH,
                    expand=True,
                    padx=Spacing.SM
                )
        else:
            # 縦並び
            for child_info in self._children:
                child_info['widget'].pack(
                    side=TOP,
                    fill=BOTH,
                    expand=True,
                    pady=Spacing.SM
                )


class ResponsiveGrid(ttk.Frame):
    """幅に応じて列数を自動調整するグリッドコンテナ"""

    def __init__(
        self,
        parent,
        min_item_width: int = 300,
        max_columns: int = 4,
        **kwargs
    ):
        """
        Args:
            parent: 親ウィジェット
            min_item_width: 各アイテムの最小幅
            max_columns: 最大列数
        """
        super().__init__(parent, **kwargs)

        self.min_item_width = min_item_width
        self.max_columns = max_columns
        self._children = []
        self._last_columns = None
        self._resize_job = None

        self.bind('<Configure>', self._on_resize)

    def add_child(self, widget):
        """子ウィジェットを追加"""
        self._children.append(widget)

        # 初期配置
        idx = len(self._children) - 1
        row = idx // self.max_columns
        col = idx % self.max_columns

        widget.grid(row=row, column=col, padx=Spacing.SM, pady=Spacing.SM, sticky='nsew')

        # 列の重みを設定
        self.columnconfigure(col, weight=1)
        self.rowconfigure(row, weight=1)

    def _on_resize(self, event):
        """リサイズイベント処理"""
        if event.width < 100:
            return

        # 列数を計算
        columns = max(1, min(self.max_columns, event.width // self.min_item_width))

        if self._last_columns == columns:
            return

        self._last_columns = columns

        # 既存のジョブをキャンセル
        if self._resize_job:
            self.after_cancel(self._resize_job)

        # 100ms後に再配置（デバウンス）
        self._resize_job = self.after(100, lambda: self._relayout(columns))

    def _relayout(self, columns: int):
        """レイアウトを再構築"""
        # 全ての子ウィジェットのgridを解除
        for widget in self._children:
            widget.grid_forget()

        # 再配置
        for idx, widget in enumerate(self._children):
            row = idx // columns
            col = idx % columns

            widget.grid(
                row=row,
                column=col,
                padx=Spacing.SM,
                pady=Spacing.SM,
                sticky='nsew'
            )

        # 列の重みをリセットしてから設定
        for i in range(self.max_columns):
            self.columnconfigure(i, weight=0)

        for i in range(columns):
            self.columnconfigure(i, weight=1, uniform='grid')

        # 行の重みを設定
        rows = (len(self._children) + columns - 1) // columns
        for i in range(rows):
            self.rowconfigure(i, weight=1)


class AdaptiveScrollFrame(ttk.Frame):
    """スクロール可能なフレーム（改良版）"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # キャンバスとスクロールバー
        self.canvas = tk.Canvas(self, bg=Colors.BG_MAIN, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        # スクロール領域の設定
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor=NW
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # マウスホイールでスクロール
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)  # Linux
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)  # Linux

        # レイアウト
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        # キャンバスリサイズ時にフレーム幅を調整
        self.canvas.bind('<Configure>', self._on_canvas_configure)

    def _on_canvas_configure(self, event):
        """キャンバスリサイズ時の処理"""
        # scrollable_frameの幅をキャンバス幅に合わせる
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        """マウスホイールスクロール"""
        # Linuxの場合
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            # Windows/macOS
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def get_frame(self) -> ttk.Frame:
        """スクロール可能なフレームを返す"""
        return self.scrollable_frame
