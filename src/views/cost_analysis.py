"""原価分析画面 - レスポンシブ対応版"""
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from ..data_processor import DataProcessor
from ..components.kpi_card import format_currency
from ..components.charts import PieChart, BarChart, StackedBarChart
from ..components.responsive import ResponsiveRow, AdaptiveScrollFrame
from ..components.theme import Colors, Fonts, Spacing, ChartColors


class CostAnalysisView(ttk.Frame):
    """原価分析画面"""

    def __init__(self, parent, processor: DataProcessor, **kwargs):
        super().__init__(parent, **kwargs)

        self.processor = processor

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
            text="💹 原価分析",
            font=(Fonts.FAMILY, Fonts.SIZE_TITLE, 'bold'),
            fg=Colors.PRIMARY,
            bg=Colors.BG_MAIN
        ).pack(side=LEFT)

        # 製造原価セクション（レスポンシブ）
        cost_section = ttk.LabelFrame(content, text="  製造原価構成（全社）  ")
        cost_section.pack(fill=X, padx=Spacing.CONTENT_MARGIN, pady=Spacing.MD)

        self.cost_row = ResponsiveRow(cost_section, breakpoint=700)
        self.cost_row.pack(fill=X, padx=Spacing.MD, pady=Spacing.MD)

        # 左: 円グラフ
        cost_left = ttk.Frame(self.cost_row)
        self.cost_pie = PieChart(cost_left, figsize=(4, 3))
        self.cost_pie.pack(fill=BOTH, expand=True)
        self.cost_row.add_child(cost_left, weight=1)

        # 右: サマリー
        cost_right = ttk.Frame(self.cost_row)
        self.cost_summary_frame = ttk.Frame(cost_right)
        self.cost_summary_frame.pack(fill=BOTH, expand=True)
        self.cost_row.add_child(cost_right, weight=1)

        # 部門別原価比較セクション（レスポンシブ）
        dept_section = ttk.LabelFrame(content, text="  部門別製造原価比較  ")
        dept_section.pack(fill=BOTH, expand=True, padx=Spacing.CONTENT_MARGIN, pady=Spacing.MD)

        self.dept_row = ResponsiveRow(dept_section, breakpoint=850)
        self.dept_row.pack(fill=BOTH, expand=True, padx=Spacing.MD, pady=Spacing.MD)

        # 左: 部門別原価合計
        dept_left = ttk.Frame(self.dept_row)
        self.dept_bar = BarChart(dept_left, figsize=(5, 4))
        self.dept_bar.pack(fill=BOTH, expand=True)
        self.dept_row.add_child(dept_left, weight=1)

        # 右: 部門別原価構成（積み上げ）
        dept_right = ttk.Frame(self.dept_row)
        self.stacked_bar = StackedBarChart(dept_right, figsize=(5, 4))
        self.stacked_bar.pack(fill=BOTH, expand=True)
        self.dept_row.add_child(dept_right, weight=1)

        # 販管費セクション（レスポンシブ）
        sga_section = ttk.LabelFrame(content, text="  販売費及び一般管理費  ")
        sga_section.pack(fill=X, padx=Spacing.CONTENT_MARGIN, pady=Spacing.MD)

        self.sga_row = ResponsiveRow(sga_section, breakpoint=700)
        self.sga_row.pack(fill=X, padx=Spacing.MD, pady=Spacing.MD)

        # 左: 販管費グラフ
        sga_left = ttk.Frame(self.sga_row)
        self.sga_bar = BarChart(sga_left, figsize=(6, 4))
        self.sga_bar.pack(fill=BOTH, expand=True)
        self.sga_row.add_child(sga_left, weight=1)

        # 右: 販管費サマリー
        sga_right = ttk.Frame(self.sga_row)
        self.sga_summary_frame = ttk.Frame(sga_right)
        self.sga_summary_frame.pack(fill=BOTH, expand=True)
        self.sga_row.add_child(sga_right, weight=1)

    def _update_cost_summary(self, cost_data: dict):
        """原価サマリーを更新"""
        for widget in self.cost_summary_frame.winfo_children():
            widget.destroy()

        # タイトル
        title_frame = tk.Frame(self.cost_summary_frame, bg=Colors.WHITE)
        title_frame.pack(fill=X, pady=(0, Spacing.MD))

        tk.Label(
            title_frame,
            text="📋 原価内訳",
            font=(Fonts.FAMILY, Fonts.SIZE_SUBHEADING, 'bold'),
            fg=Colors.PRIMARY,
            bg=Colors.WHITE
        ).pack(anchor=W)

        total = cost_data['mfg_cost']
        items = [
            ('🔴 材料費', cost_data['material_cost'], ChartColors.COST['material']),
            ('🔵 労務費', cost_data['labor_cost'], ChartColors.COST['labor']),
            ('🟢 経費', cost_data['expense'], ChartColors.COST['expense']),
        ]

        for label, value, color in items:
            row = tk.Frame(self.cost_summary_frame, bg=Colors.WHITE)
            row.pack(fill=X, pady=3)

            tk.Label(
                row,
                text=label,
                width=12,
                anchor=W,
                font=(Fonts.FAMILY, Fonts.SIZE_BODY),
                fg=Colors.GRAY_700,
                bg=Colors.WHITE
            ).pack(side=LEFT)

            tk.Label(
                row,
                text=format_currency(value),
                width=12,
                anchor=E,
                font=(Fonts.FAMILY, Fonts.SIZE_BODY),
                fg=Colors.GRAY_800,
                bg=Colors.WHITE
            ).pack(side=LEFT, padx=(0, Spacing.SM))

            # 構成比
            ratio = (value / total * 100) if total != 0 else 0
            tk.Label(
                row,
                text=f"({ratio:.1f}%)",
                font=(Fonts.FAMILY, Fonts.SIZE_SMALL),
                fg=Colors.GRAY_500,
                bg=Colors.WHITE
            ).pack(side=LEFT)

        ttk.Separator(self.cost_summary_frame, orient=HORIZONTAL).pack(fill=X, pady=Spacing.MD)

        # 合計
        total_row = tk.Frame(self.cost_summary_frame, bg=Colors.GRAY_50)
        total_row.pack(fill=X, pady=2)

        tk.Label(
            total_row,
            text="製造原価計",
            font=(Fonts.FAMILY, Fonts.SIZE_BODY, 'bold'),
            width=12,
            anchor=W,
            fg=Colors.GRAY_800,
            bg=Colors.GRAY_50,
            pady=6
        ).pack(side=LEFT)

        tk.Label(
            total_row,
            text=format_currency(total),
            font=(Fonts.FAMILY, Fonts.SIZE_BODY, 'bold'),
            width=12,
            anchor=E,
            fg=Colors.PRIMARY,
            bg=Colors.GRAY_50,
            pady=6
        ).pack(side=LEFT)

    def _update_sga_summary(self, sga_df, total_sga: float):
        """販管費サマリーを更新"""
        for widget in self.sga_summary_frame.winfo_children():
            widget.destroy()

        # タイトル
        title_frame = tk.Frame(self.sga_summary_frame, bg=Colors.WHITE)
        title_frame.pack(fill=X, pady=(0, Spacing.MD))

        tk.Label(
            title_frame,
            text="📋 販管費内訳（上位5項目）",
            font=(Fonts.FAMILY, Fonts.SIZE_SUBHEADING, 'bold'),
            fg=Colors.PRIMARY,
            bg=Colors.WHITE
        ).pack(anchor=W)

        # 上位5項目を表示
        top_items = sga_df.head(5) if not sga_df.empty else []

        for idx, (_, item) in enumerate(top_items.iterrows()):
            row_bg = Colors.WHITE if idx % 2 == 0 else Colors.GRAY_50

            row = tk.Frame(self.sga_summary_frame, bg=row_bg)
            row.pack(fill=X)

            # 科目名（長い場合は省略）
            name = item['科目名']
            if len(name) > 12:
                name = name[:11] + '…'

            tk.Label(
                row,
                text=name,
                width=14,
                anchor=W,
                font=(Fonts.FAMILY, Fonts.SIZE_BODY),
                fg=Colors.GRAY_700,
                bg=row_bg,
                pady=4
            ).pack(side=LEFT)

            tk.Label(
                row,
                text=format_currency(item['金額']),
                width=12,
                anchor=E,
                font=(Fonts.FAMILY, Fonts.SIZE_BODY),
                fg=Colors.GRAY_800,
                bg=row_bg,
                pady=4
            ).pack(side=LEFT)

        ttk.Separator(self.sga_summary_frame, orient=HORIZONTAL).pack(fill=X, pady=Spacing.MD)

        # 合計
        total_row = tk.Frame(self.sga_summary_frame, bg=Colors.GRAY_50)
        total_row.pack(fill=X, pady=2)

        tk.Label(
            total_row,
            text="販管費計",
            font=(Fonts.FAMILY, Fonts.SIZE_BODY, 'bold'),
            width=14,
            anchor=W,
            fg=Colors.GRAY_800,
            bg=Colors.GRAY_50,
            pady=6
        ).pack(side=LEFT)

        tk.Label(
            total_row,
            text=format_currency(total_sga),
            font=(Fonts.FAMILY, Fonts.SIZE_BODY, 'bold'),
            width=12,
            anchor=E,
            fg=Colors.PRIMARY,
            bg=Colors.GRAY_50,
            pady=6
        ).pack(side=LEFT)

    def refresh(self, year_month: str = None):
        """画面を更新

        Args:
            year_month: 対象年月（Noneで全期間）
        """
        # 全社の原価構成を取得
        cost_data = self.processor.get_cost_structure(year_month=year_month)

        # 原価構成円グラフ
        cost_labels = ['材料費', '労務費', '経費']
        cost_values = [
            cost_data['material_cost'],
            cost_data['labor_cost'],
            cost_data['expense']
        ]

        # 原価分析用の専用カラー
        cost_colors = [
            ChartColors.COST['material'],
            ChartColors.COST['labor'],
            ChartColors.COST['expense']
        ]

        # 正の値のみ表示
        if any(v > 0 for v in cost_values):
            self.cost_pie.plot(
                labels=cost_labels,
                values=cost_values,
                title='製造原価構成比',
                colors=cost_colors
            )
        else:
            self.cost_pie.clear()
            self.cost_pie.draw()

        # 原価サマリー更新
        self._update_cost_summary(cost_data)

        # 部門別原価比較
        dept_cost_df = self.processor.get_cost_breakdown_by_dept(year_month=year_month)

        # 「共通」部門を除外
        dept_cost_df = dept_cost_df[dept_cost_df['部課名'] != '共通']

        if not dept_cost_df.empty:
            # 部門別製造原価合計
            self.dept_bar.plot(
                labels=dept_cost_df['部課名'].tolist(),
                values=dept_cost_df['製造原価'].tolist(),
                title='部門別製造原価',
                ylabel='円',
                color='#8b5cf6'
            )

            # 部門別原価構成（積み上げ棒グラフ）
            self.stacked_bar.plot(
                labels=dept_cost_df['部課名'].tolist(),
                data_dict={
                    '材料費': dept_cost_df['材料費'].tolist(),
                    '労務費': dept_cost_df['労務費'].tolist(),
                    '経費': dept_cost_df['経費'].tolist()
                },
                title='部門別原価構成',
                ylabel='円',
                colors=[
                    ChartColors.COST['material'],
                    ChartColors.COST['labor'],
                    ChartColors.COST['expense']
                ]
            )
        else:
            self.dept_bar.clear()
            self.dept_bar.draw()
            self.stacked_bar.clear()
            self.stacked_bar.draw()

        # 販管費分析
        kpi = self.processor.calculate_kpi(year_month=year_month)
        total_sga = kpi['sga']

        sga_df = self.processor.get_sga_breakdown(year_month=year_month)

        if not sga_df.empty:
            # 上位10項目を棒グラフで表示
            top_sga = sga_df.head(10)

            self.sga_bar.plot(
                labels=top_sga['科目名'].tolist(),
                values=top_sga['金額'].tolist(),
                title='販管費内訳（上位10項目）',
                ylabel='円',
                color='#f59e0b',
                horizontal=True
            )
        else:
            self.sga_bar.clear()
            self.sga_bar.draw()

        # 販管費サマリー更新
        self._update_sga_summary(sga_df, total_sga)
