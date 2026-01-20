"""部門別分析画面 - レスポンシブ対応版"""
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from ..data_loader import DataLoader
from ..data_processor import DataProcessor
from ..components.kpi_card import KPICardGroup, format_currency
from ..components.charts import BarChart, LineChart
from ..components.responsive import ResponsiveRow, AdaptiveScrollFrame
from ..components.theme import Colors, Fonts, Spacing


class DepartmentView(ttk.Frame):
    """部門別分析画面"""

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
        self.selected_dept_code = None

        self._create_widgets()
        self.refresh()

    def _create_widgets(self):
        """ウィジェットを作成"""
        # スクロール可能なフレーム（レスポンシブ対応）
        self.scroll_frame = AdaptiveScrollFrame(self)
        self.scroll_frame.pack(fill=BOTH, expand=True)

        content = self.scroll_frame.get_frame()

        # ヘッダー
        header = tk.Frame(content, bg=Colors.BG_MAIN)
        header.pack(fill=X, padx=Spacing.CONTENT_MARGIN, pady=(Spacing.CONTENT_MARGIN, Spacing.MD))

        tk.Label(
            header,
            text="🏢 部門別分析",
            font=(Fonts.FAMILY, Fonts.SIZE_TITLE, 'bold'),
            fg=Colors.PRIMARY,
            bg=Colors.BG_MAIN
        ).pack(side=LEFT)

        # 部門選択
        select_frame = tk.Frame(header, bg=Colors.BG_MAIN)
        select_frame.pack(side=RIGHT)

        tk.Label(
            select_frame,
            text="📁 部門選択:",
            font=(Fonts.FAMILY, Fonts.SIZE_BODY),
            fg=Colors.GRAY_600,
            bg=Colors.BG_MAIN
        ).pack(side=LEFT, padx=(0, 8))

        self.dept_var = ttk.StringVar()
        self.dept_combo = ttk.Combobox(
            select_frame,
            textvariable=self.dept_var,
            width=20,
            state="readonly",
            font=(Fonts.FAMILY, Fonts.SIZE_BODY)
        )
        self.dept_combo.pack(side=LEFT)
        self.dept_combo.bind("<<ComboboxSelected>>", self._on_dept_change)

        # 部門リストを設定
        self._update_dept_combo()

        # KPIカードセクション
        kpi_section = ttk.LabelFrame(content, text="  主要KPI  ")
        kpi_section.pack(fill=X, padx=Spacing.CONTENT_MARGIN, pady=Spacing.MD)

        self.kpi_group = KPICardGroup(kpi_section)
        self.kpi_group.pack(fill=X, padx=Spacing.MD, pady=Spacing.MD)

        # グラフセクション（レスポンシブ）
        self.charts_row = ResponsiveRow(content, breakpoint=850)
        self.charts_row.pack(fill=BOTH, expand=True, padx=Spacing.CONTENT_MARGIN, pady=Spacing.MD)

        # 左: 売上・利益推移
        left_frame = ttk.LabelFrame(self.charts_row, text="  月次推移  ")
        self.line_chart = LineChart(left_frame, figsize=(5, 4))
        self.line_chart.pack(fill=BOTH, expand=True, padx=Spacing.MD, pady=Spacing.MD)
        self.charts_row.add_child(left_frame, weight=1)

        # 右: 利益構成
        right_frame = ttk.LabelFrame(self.charts_row, text="  利益構成  ")
        self.bar_chart = BarChart(right_frame, figsize=(5, 4))
        self.bar_chart.pack(fill=BOTH, expand=True, padx=Spacing.MD, pady=Spacing.MD)
        self.charts_row.add_child(right_frame, weight=1)

        # サマリーテーブル
        table_section = ttk.LabelFrame(content, text="  経営指標サマリー  ")
        table_section.pack(fill=X, padx=Spacing.CONTENT_MARGIN, pady=Spacing.MD)

        table_inner = ttk.Frame(table_section)
        table_inner.pack(fill=X, padx=Spacing.MD, pady=Spacing.MD)

        self._create_summary_table(table_inner)

    def _update_dept_combo(self):
        """部門コンボボックスを更新"""
        departments = self.loader.get_departments()

        if departments:
            # 「共通」部門を除外
            departments = [(code, name) for code, name in departments if name != '共通']
            self.departments = departments
            values = [name for _, name in departments]
            self.dept_combo["values"] = values
            if values:
                self.dept_var.set(values[0])
                self.selected_dept_code = departments[0][0]
        else:
            self.departments = []
            self.dept_combo["values"] = ["データなし"]
            self.dept_var.set("データなし")

    def _on_dept_change(self, event):
        """部門変更時のコールバック"""
        selected = self.dept_var.get()
        for code, name in self.departments:
            if name == selected:
                self.selected_dept_code = code
                break
        self.refresh()

    def _create_summary_table(self, parent):
        """サマリーテーブルを作成"""
        columns = ['指標', '値', '説明']

        header_frame = tk.Frame(parent, bg=Colors.GRAY_100)
        header_frame.pack(fill=X)

        widths = [15, 15, 45]
        for i, col in enumerate(columns):
            label = tk.Label(
                header_frame,
                text=col,
                font=(Fonts.FAMILY, Fonts.SIZE_SMALL, 'bold'),
                width=widths[i],
                anchor=W if i == 2 else CENTER,
                bg=Colors.GRAY_100,
                fg=Colors.GRAY_700,
                pady=8
            )
            label.pack(side=LEFT, padx=2)

        ttk.Separator(parent, orient=HORIZONTAL).pack(fill=X)

        self.table_data_frame = ttk.Frame(parent)
        self.table_data_frame.pack(fill=X)

    def _update_summary_table(self, kpi: dict):
        """サマリーテーブルを更新"""
        for widget in self.table_data_frame.winfo_children():
            widget.destroy()

        # (ラベル, 値, 元の数値, 説明) のタプル
        rows = [
            ('売上高', format_currency(kpi['revenue']), kpi['revenue'], '当期の総売上高'),
            ('売上原価', format_currency(kpi['cost_of_sales']), kpi['cost_of_sales'], '製品製造に直接かかった費用'),
            ('売上総利益', format_currency(kpi['gross_profit']), kpi['gross_profit'], '売上高から売上原価を差し引いた利益'),
            ('売上総利益率', f"{kpi['gross_margin']:.1f}%", kpi['gross_margin'], '売上高に対する売上総利益の割合'),
            ('販管費', format_currency(kpi['sga']), kpi['sga'], '販売費及び一般管理費'),
            ('営業利益', format_currency(kpi['operating_income']), kpi['operating_income'], '本業での利益'),
            ('営業利益率', f"{kpi['op_margin']:.1f}%", kpi['op_margin'], '売上高に対する営業利益の割合'),
            ('経常利益', format_currency(kpi['ordinary_income']), kpi['ordinary_income'], '経常的な活動による利益'),
            ('経常利益率', f"{kpi['ord_margin']:.1f}%", kpi['ord_margin'], '売上高に対する経常利益の割合'),
        ]

        for idx, (label, value, raw_value, desc) in enumerate(rows):
            row_bg = Colors.WHITE if idx % 2 == 0 else Colors.GRAY_50

            row_frame = tk.Frame(self.table_data_frame, bg=row_bg)
            row_frame.pack(fill=X)

            # 指標名
            tk.Label(
                row_frame,
                text=label,
                width=15,
                anchor=W,
                bg=row_bg,
                fg=Colors.GRAY_800,
                font=(Fonts.FAMILY, Fonts.SIZE_BODY),
                pady=6
            ).pack(side=LEFT, padx=2)

            # 値（赤字の場合は色を変える）
            is_negative = raw_value < 0
            value_color = Colors.DANGER if is_negative else Colors.GRAY_700

            tk.Label(
                row_frame,
                text=value,
                width=15,
                anchor=E,
                bg=row_bg,
                fg=value_color,
                font=(Fonts.FAMILY, Fonts.SIZE_BODY, 'bold') if is_negative else (Fonts.FAMILY, Fonts.SIZE_BODY),
                pady=6
            ).pack(side=LEFT, padx=2)

            # 説明
            tk.Label(
                row_frame,
                text=desc,
                width=45,
                anchor=W,
                bg=row_bg,
                fg=Colors.GRAY_500,
                font=(Fonts.FAMILY, Fonts.SIZE_SMALL),
                pady=6
            ).pack(side=LEFT, padx=2)

    def refresh(self, year_month: str = None):
        """画面を更新

        Args:
            year_month: 対象年月（Noneで全期間）
        """
        if self.selected_dept_code is None:
            return

        # KPIを計算
        kpi = self.processor.calculate_kpi(
            dept_code=self.selected_dept_code,
            year_month=year_month
        )

        # KPIカードを更新
        if not self.kpi_group.cards:
            self.kpi_group.add_card(
                'revenue',
                title='売上高',
                value=kpi['revenue'],
                rate=None,
                bootstyle='primary'
            )
            self.kpi_group.add_card(
                'gross_profit',
                title='売上総利益',
                value=kpi['gross_profit'],
                rate=kpi['gross_margin'],
                rate_label='利益率',
                bootstyle='info'
            )
            self.kpi_group.add_card(
                'operating_income',
                title='営業利益',
                value=kpi['operating_income'],
                rate=kpi['op_margin'],
                rate_label='利益率',
                bootstyle='success'
            )
            self.kpi_group.add_card(
                'ordinary_income',
                title='経常利益',
                value=kpi['ordinary_income'],
                rate=kpi['ord_margin'],
                rate_label='利益率',
                bootstyle='warning'
            )
        else:
            self.kpi_group.update_card('revenue', kpi['revenue'])
            self.kpi_group.update_card('gross_profit', kpi['gross_profit'], kpi['gross_margin'])
            self.kpi_group.update_card('operating_income', kpi['operating_income'], kpi['op_margin'])
            self.kpi_group.update_card('ordinary_income', kpi['ordinary_income'], kpi['ord_margin'])

        # 月次推移グラフ
        periods = self.loader.get_periods()
        if len(periods) > 1:
            revenues = []
            op_incomes = []
            for period in periods:
                p_kpi = self.processor.calculate_kpi(
                    dept_code=self.selected_dept_code,
                    year_month=period
                )
                revenues.append(p_kpi['revenue'] / 1_000_000)  # 百万円単位
                op_incomes.append(p_kpi['operating_income'] / 1_000_000)

            self.line_chart.plot(
                x_data=periods,
                y_data_dict={
                    '売上高': revenues,
                    '営業利益': op_incomes
                },
                title='月次推移',
                xlabel='期間',
                ylabel='百万円'
            )
        else:
            self.line_chart.clear()
            self.line_chart.draw()

        # 利益構成グラフ
        profit_data = [
            ('売上総利益', kpi['gross_profit']),
            ('営業利益', kpi['operating_income']),
            ('経常利益', kpi['ordinary_income']),
        ]
        labels = [d[0] for d in profit_data]
        values = [d[1] for d in profit_data]

        self.bar_chart.plot(
            labels=labels,
            values=values,
            title='利益構成',
            ylabel='円',
            color='#10b981'
        )

        # サマリーテーブル更新
        self._update_summary_table(kpi)
