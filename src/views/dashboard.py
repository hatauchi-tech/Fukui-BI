"""全社サマリーダッシュボード - レスポンシブ対応版"""
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from ..data_processor import DataProcessor
from ..components.kpi_card import KPICardGroup, format_currency
from ..components.charts import BarChart, PieChart
from ..components.responsive import ResponsiveRow, AdaptiveScrollFrame
from ..components.theme import Colors, Fonts, Spacing


class DashboardView(ttk.Frame):
    """全社サマリー画面（レスポンシブ対応）"""

    def __init__(self, parent, processor: DataProcessor, **kwargs):
        super().__init__(parent, **kwargs)

        self.processor = processor
        self._create_widgets()
        self.refresh()

    def _create_widgets(self):
        """ウィジェットを作成"""
        # スクロール可能なフレーム
        self.scroll_frame = AdaptiveScrollFrame(self)
        self.scroll_frame.pack(fill=BOTH, expand=True)

        content = self.scroll_frame.get_frame()

        # タイトルセクション
        header = tk.Frame(content, bg=Colors.BG_MAIN)
        header.pack(fill=X, padx=Spacing.CONTENT_MARGIN, pady=(Spacing.CONTENT_MARGIN, Spacing.MD))

        tk.Label(
            header,
            text="📊 経営ダッシュボード",
            font=(Fonts.FAMILY, Fonts.SIZE_TITLE, 'bold'),
            fg=Colors.PRIMARY,
            bg=Colors.BG_MAIN
        ).pack(side=LEFT)

        # KPIカードセクション
        kpi_section = ttk.LabelFrame(content, text="  主要KPI  ")
        kpi_section.pack(fill=X, padx=Spacing.CONTENT_MARGIN, pady=Spacing.MD)

        self.kpi_group = KPICardGroup(kpi_section)
        self.kpi_group.pack(fill=X, padx=Spacing.MD, pady=Spacing.MD)

        # グラフセクション（レスポンシブ）
        self.charts_row = ResponsiveRow(content, breakpoint=850)
        self.charts_row.pack(fill=BOTH, expand=True, padx=Spacing.CONTENT_MARGIN, pady=Spacing.MD)

        # 左: 部門別売上構成比（円グラフ）
        left_frame = ttk.LabelFrame(self.charts_row, text="  部門別売上構成比  ")
        self.pie_chart = PieChart(left_frame, figsize=(5, 4))
        self.pie_chart.pack(fill=BOTH, expand=True, padx=Spacing.MD, pady=Spacing.MD)
        self.charts_row.add_child(left_frame, weight=1)

        # 右: 部門別利益比較（棒グラフ）
        right_frame = ttk.LabelFrame(self.charts_row, text="  部門別営業利益  ")
        self.bar_chart = BarChart(right_frame, figsize=(5, 4))
        self.bar_chart.pack(fill=BOTH, expand=True, padx=Spacing.MD, pady=Spacing.MD)
        self.charts_row.add_child(right_frame, weight=1)

        # 部門別詳細テーブル
        table_section = ttk.LabelFrame(content, text="  部門別サマリー  ")
        table_section.pack(fill=X, padx=Spacing.CONTENT_MARGIN, pady=Spacing.MD)

        # テーブルコンテナ（横スクロール対応）
        table_container = ttk.Frame(table_section)
        table_container.pack(fill=X, padx=Spacing.MD, pady=Spacing.MD)

        self._create_summary_table(table_container)

    def _create_summary_table(self, parent):
        """サマリーテーブルを作成"""
        columns = ['部門', '売上高', '売上総利益', '営業利益', '売上総利益率', '営業利益率']

        header_frame = tk.Frame(parent, bg=Colors.GRAY_100)
        header_frame.pack(fill=X)

        for i, col in enumerate(columns):
            label = tk.Label(
                header_frame,
                text=col,
                font=(Fonts.FAMILY, Fonts.SIZE_SMALL, 'bold'),
                width=15 if i > 0 else 12,
                anchor=E if i > 0 else W,
                bg=Colors.GRAY_100,
                fg=Colors.GRAY_700,
                pady=8
            )
            label.pack(side=LEFT, padx=2)

        ttk.Separator(parent, orient=HORIZONTAL).pack(fill=X)

        self.table_data_frame = ttk.Frame(parent)
        self.table_data_frame.pack(fill=X)

    def _update_summary_table(self, dept_df):
        """サマリーテーブルを更新"""
        for widget in self.table_data_frame.winfo_children():
            widget.destroy()

        display_df = dept_df[dept_df['部課名'] != '共通']

        for idx, (_, row) in enumerate(display_df.iterrows()):
            row_bg = Colors.WHITE if idx % 2 == 0 else Colors.GRAY_50

            row_frame = tk.Frame(self.table_data_frame, bg=row_bg)
            row_frame.pack(fill=X)

            # 部門名
            tk.Label(
                row_frame,
                text=row['部課名'],
                width=12,
                anchor=W,
                bg=row_bg,
                fg=Colors.GRAY_800,
                font=(Fonts.FAMILY, Fonts.SIZE_BODY),
                pady=6
            ).pack(side=LEFT, padx=2)

            # 売上高
            tk.Label(
                row_frame,
                text=format_currency(row['売上高']),
                width=15,
                anchor=E,
                bg=row_bg,
                fg=Colors.GRAY_700,
                font=(Fonts.FAMILY, Fonts.SIZE_BODY),
                pady=6
            ).pack(side=LEFT, padx=2)

            # 売上総利益
            gp_color = Colors.DANGER if row['売上総利益'] < 0 else Colors.GRAY_700
            tk.Label(
                row_frame,
                text=format_currency(row['売上総利益']),
                width=15,
                anchor=E,
                bg=row_bg,
                fg=gp_color,
                font=(Fonts.FAMILY, Fonts.SIZE_BODY),
                pady=6
            ).pack(side=LEFT, padx=2)

            # 営業利益
            op_color = Colors.DANGER if row['営業利益'] < 0 else Colors.GRAY_700
            tk.Label(
                row_frame,
                text=format_currency(row['営業利益']),
                width=15,
                anchor=E,
                bg=row_bg,
                fg=op_color,
                font=(Fonts.FAMILY, Fonts.SIZE_BODY, 'bold') if row['営業利益'] < 0 else (Fonts.FAMILY, Fonts.SIZE_BODY),
                pady=6
            ).pack(side=LEFT, padx=2)

            # 売上総利益率
            gm_color = Colors.DANGER if row['売上総利益率'] < 0 else Colors.GRAY_700
            tk.Label(
                row_frame,
                text=f"{row['売上総利益率']:.1f}%",
                width=15,
                anchor=E,
                bg=row_bg,
                fg=gm_color,
                font=(Fonts.FAMILY, Fonts.SIZE_BODY),
                pady=6
            ).pack(side=LEFT, padx=2)

            # 営業利益率
            op_margin_color = Colors.DANGER if row['営業利益率'] < 0 else Colors.GRAY_700
            tk.Label(
                row_frame,
                text=f"{row['営業利益率']:.1f}%",
                width=15,
                anchor=E,
                bg=row_bg,
                fg=op_margin_color,
                font=(Fonts.FAMILY, Fonts.SIZE_BODY),
                pady=6
            ).pack(side=LEFT, padx=2)

    def refresh(self, year_month: str = None):
        """画面を更新"""
        kpi = self.processor.calculate_kpi(year_month=year_month)

        if not self.kpi_group.cards:
            self.kpi_group.add_card('revenue', title='売上高', value=kpi['revenue'], rate=None, bootstyle='primary')
            self.kpi_group.add_card('gross_profit', title='売上総利益', value=kpi['gross_profit'], rate=kpi['gross_margin'], rate_label='利益率', bootstyle='info')
            self.kpi_group.add_card('operating_income', title='営業利益', value=kpi['operating_income'], rate=kpi['op_margin'], rate_label='利益率', bootstyle='success')
            self.kpi_group.add_card('ordinary_income', title='経常利益', value=kpi['ordinary_income'], rate=kpi['ord_margin'], rate_label='利益率', bootstyle='warning')
        else:
            self.kpi_group.update_card('revenue', kpi['revenue'])
            self.kpi_group.update_card('gross_profit', kpi['gross_profit'], kpi['gross_margin'])
            self.kpi_group.update_card('operating_income', kpi['operating_income'], kpi['op_margin'])
            self.kpi_group.update_card('ordinary_income', kpi['ordinary_income'], kpi['ord_margin'])

        dept_df = self.processor.get_department_breakdown(year_month=year_month)
        chart_df = dept_df[dept_df['部課名'] != '共通']
        positive_revenue_df = chart_df[chart_df['売上高'] > 0]

        if not positive_revenue_df.empty:
            self.pie_chart.plot(
                labels=positive_revenue_df['部課名'].tolist(),
                values=positive_revenue_df['売上高'].tolist(),
                title='部門別売上構成比'
            )
        else:
            self.pie_chart.clear()
            self.pie_chart.draw()

        if not chart_df.empty:
            self.bar_chart.plot(
                labels=chart_df['部課名'].tolist(),
                values=chart_df['営業利益'].tolist(),
                title='部門別営業利益',
                ylabel='円',
                color='#10b981'
            )
        else:
            self.bar_chart.clear()
            self.bar_chart.draw()

        self._update_summary_table(dept_df)
