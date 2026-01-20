"""KPIカードコンポーネント - レスポンシブ対応版"""
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from .theme import Colors, KPIColors, Fonts, Spacing


def format_currency(value: float) -> str:
    """金額を日本円形式でフォーマット"""
    if abs(value) >= 1_000_000_000:
        return f"¥{value / 1_000_000_000:.2f}億"
    elif abs(value) >= 1_000_000:
        return f"¥{value / 1_000_000:.1f}百万"
    elif abs(value) >= 1_000:
        return f"¥{value / 1_000:.0f}千"
    else:
        return f"¥{value:,.0f}"


class KPICard(tk.Frame):
    """KPI表示用カード - レスポンシブ対応"""

    KPI_THEMES = {
        'revenue': KPIColors.REVENUE,
        'gross_profit': KPIColors.GROSS_PROFIT,
        'operating_income': KPIColors.OPERATING_INCOME,
        'ordinary_income': KPIColors.ORDINARY_INCOME,
    }

    def __init__(
        self,
        parent,
        title: str,
        value: float,
        rate: float = None,
        rate_label: str = None,
        kpi_type: str = 'revenue',
        **kwargs
    ):
        self.theme = self.KPI_THEMES.get(kpi_type, KPIColors.REVENUE)

        super().__init__(
            parent,
            bg=self.theme['bg'],
            highlightbackground=self.theme['accent'],
            highlightthickness=2,
            **kwargs
        )

        self.title = title
        self.value = value
        self.rate = rate
        self.rate_label = rate_label
        self.kpi_type = kpi_type

        self._create_widgets()

        # リサイズ対応
        self.bind('<Configure>', self._on_resize)
        self._last_width = None

    def _on_resize(self, event):
        """リサイズ時にフォントサイズを調整"""
        if event.width < 50:
            return

        if self._last_width == event.width:
            return

        self._last_width = event.width

        # 幅に応じてフォントサイズを調整
        if event.width < 180:
            value_size = 16
            title_size = 9
            rate_size = 8
        elif event.width < 220:
            value_size = 18
            title_size = 10
            rate_size = 9
        else:
            value_size = 22
            title_size = 11
            rate_size = 10

        # フォント更新
        self.value_label.configure(font=(Fonts.FAMILY, value_size, 'bold'))
        self.title_label.configure(font=(Fonts.FAMILY, title_size))

        if hasattr(self, 'rate_value_label'):
            self.rate_value_label.configure(font=(Fonts.FAMILY, rate_size, 'bold'))

    def _create_widgets(self):
        """ウィジェットを作成"""
        theme = self.theme
        padding = Spacing.CARD_PADDING

        container = tk.Frame(self, bg=theme['bg'])
        container.pack(fill=BOTH, expand=True, padx=padding, pady=padding)

        # ヘッダー行（アイコン + タイトル）
        header = tk.Frame(container, bg=theme['bg'])
        header.pack(fill=X, pady=(0, 6))

        self.icon_label = tk.Label(
            header,
            text=theme['icon'],
            font=(Fonts.FAMILY, 12),
            bg=theme['bg']
        )
        self.icon_label.pack(side=LEFT)

        self.title_label = tk.Label(
            header,
            text=self.title,
            font=(Fonts.FAMILY, Fonts.SIZE_KPI_TITLE),
            fg=theme['text'],
            bg=theme['bg']
        )
        self.title_label.pack(side=LEFT, padx=(4, 0))

        # 金額
        formatted_value = format_currency(self.value)
        value_color = theme['text'] if self.value >= 0 else Colors.DANGER

        self.value_label = tk.Label(
            container,
            text=formatted_value,
            font=(Fonts.FAMILY, Fonts.SIZE_KPI_VALUE, 'bold'),
            fg=value_color,
            bg=theme['bg']
        )
        self.value_label.pack(anchor=W, pady=(0, 2))

        # 率（オプション）
        if self.rate is not None:
            rate_frame = tk.Frame(container, bg=theme['bg'])
            rate_frame.pack(fill=X)

            if self.rate_label:
                rate_label_widget = tk.Label(
                    rate_frame,
                    text=f"{self.rate_label}:",
                    font=(Fonts.FAMILY, Fonts.SIZE_KPI_RATE),
                    fg=Colors.GRAY_500,
                    bg=theme['bg']
                )
                rate_label_widget.pack(side=LEFT)

            rate_text = f"{self.rate:+.1f}%" if self.rate != 0 else "0.0%"
            rate_color = Colors.SUCCESS if self.rate > 0 else (Colors.DANGER if self.rate < 0 else Colors.GRAY_500)

            self.rate_value_label = tk.Label(
                rate_frame,
                text=rate_text,
                font=(Fonts.FAMILY, Fonts.SIZE_KPI_RATE, 'bold'),
                fg=rate_color,
                bg=theme['bg']
            )
            self.rate_value_label.pack(side=LEFT, padx=(3, 0))

            trend_icon = "▲" if self.rate > 0 else ("▼" if self.rate < 0 else "━")
            self.trend_label = tk.Label(
                rate_frame,
                text=trend_icon,
                font=(Fonts.FAMILY, Fonts.SIZE_SMALL),
                fg=rate_color,
                bg=theme['bg']
            )
            self.trend_label.pack(side=LEFT, padx=(3, 0))

    def update_values(self, value: float, rate: float = None):
        """値を更新"""
        self.value = value
        self.rate = rate

        formatted_value = format_currency(self.value)
        value_color = self.theme['text'] if self.value >= 0 else Colors.DANGER
        self.value_label.configure(text=formatted_value, fg=value_color)

        if rate is not None and hasattr(self, 'rate_value_label'):
            rate_text = f"{rate:+.1f}%" if rate != 0 else "0.0%"
            rate_color = Colors.SUCCESS if rate > 0 else (Colors.DANGER if rate < 0 else Colors.GRAY_500)
            self.rate_value_label.configure(text=rate_text, fg=rate_color)

            if hasattr(self, 'trend_label'):
                trend_icon = "▲" if rate > 0 else ("▼" if rate < 0 else "━")
                self.trend_label.configure(text=trend_icon, fg=rate_color)


class KPICardGroup(ttk.Frame):
    """複数のKPIカードをグループ化（レスポンシブGrid対応）"""

    # ブレークポイント
    BREAKPOINT_4COL = 900  # 4列
    BREAKPOINT_3COL = 700  # 3列
    BREAKPOINT_2COL = 500  # 2列
    # それ以下は1列

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.cards: dict[str, KPICard] = {}
        self._card_order = []  # カードの追加順序を保持

        # リサイズ対応
        self._resize_job = None
        self._last_columns = None
        self.bind('<Configure>', self._on_resize)

    def _on_resize(self, event):
        """リサイズ時にレイアウトを調整"""
        if event.width < 100:
            return

        # 列数を決定
        if event.width >= self.BREAKPOINT_4COL:
            columns = 4
        elif event.width >= self.BREAKPOINT_3COL:
            columns = 3
        elif event.width >= self.BREAKPOINT_2COL:
            columns = 2
        else:
            columns = 1

        # 列数が変わった場合のみ再配置
        if self._last_columns != columns:
            self._last_columns = columns

            # 既存のジョブをキャンセル
            if self._resize_job:
                self.after_cancel(self._resize_job)

            # 100ms後に再配置（デバウンス）
            self._resize_job = self.after(100, lambda: self._relayout(columns))

    def _relayout(self, columns: int):
        """カードを再配置"""
        if not self._card_order:
            return

        # 全カードのpack/gridを解除
        for key in self._card_order:
            if key in self.cards:
                self.cards[key].pack_forget()
                self.cards[key].grid_forget()

        # Gridで再配置
        for idx, key in enumerate(self._card_order):
            if key in self.cards:
                row = idx // columns
                col = idx % columns

                self.cards[key].grid(
                    row=row,
                    column=col,
                    padx=4,
                    pady=4,
                    sticky='nsew'
                )

        # 列の重みを設定（均等に伸縮）
        for i in range(columns):
            self.columnconfigure(i, weight=1, uniform='kpi')

        # 行の重みを設定
        rows = (len(self._card_order) + columns - 1) // columns
        for i in range(rows):
            self.rowconfigure(i, weight=1)

    def add_card(
        self,
        key: str,
        title: str,
        value: float,
        rate: float = None,
        rate_label: str = None,
        bootstyle: str = "primary"
    ) -> KPICard:
        """カードを追加"""
        kpi_type_map = {
            'revenue': 'revenue',
            'gross_profit': 'gross_profit',
            'operating_income': 'operating_income',
            'ordinary_income': 'ordinary_income',
        }
        kpi_type = kpi_type_map.get(key, 'revenue')

        card = KPICard(
            self,
            title=title,
            value=value,
            rate=rate,
            rate_label=rate_label,
            kpi_type=kpi_type
        )

        self.cards[key] = card
        self._card_order.append(key)

        # 初期配置
        columns = 4  # デフォルトは4列
        idx = len(self._card_order) - 1
        row = idx // columns
        col = idx % columns

        card.grid(row=row, column=col, padx=4, pady=4, sticky='nsew')

        # 列の重みを設定
        for i in range(min(columns, len(self._card_order))):
            self.columnconfigure(i, weight=1, uniform='kpi')

        return card

    def update_card(self, key: str, value: float, rate: float = None):
        """カードの値を更新"""
        if key in self.cards:
            self.cards[key].update_values(value, rate)
