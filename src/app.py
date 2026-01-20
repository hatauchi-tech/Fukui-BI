"""メインアプリケーション - 改善版デザイン"""
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime

from .data_loader import DataLoader
from .data_processor import DataProcessor
from .views.dashboard import DashboardView
from .views.department import DepartmentView
from .views.cost_analysis import CostAnalysisView
from .views.detail_view import DetailView
from .views.guide import GuideView
from .components.theme import Colors, Fonts, Spacing


class Application(ttk.Window):
    """損益計算書BIツール メインアプリケーション - 改善版"""

    def __init__(self):
        super().__init__(
            title="福井鐵工株式会社 損益計算書BIツール",
            themename="cosmo",
            size=(1280, 850),
            minsize=(800, 600)  # レスポンシブ対応により最小サイズを縮小
        )

        # データ読み込み
        self.loader = DataLoader()
        self.processor = DataProcessor(self.loader.df)

        # メイン背景色を設定
        self.configure(background=Colors.BG_MAIN)

        # ウィジェット作成
        self._create_header()
        self._create_notebook()
        self._create_statusbar()

        # 初期更新
        self._update_period_combo()

    def _create_header(self):
        """ブランディングヘッダーを作成（レスポンシブ対応）"""
        # ヘッダーコンテナ（暗い背景）
        self.header = tk.Frame(self, bg=Colors.BG_HEADER)
        self.header.pack(fill=X)

        # ヘッダー内部コンテナ
        header_inner = tk.Frame(self.header, bg=Colors.BG_HEADER)
        header_inner.pack(fill=X, padx=Spacing.MD, pady=Spacing.SM)

        # 左側: ブランディング
        self.brand_frame = tk.Frame(header_inner, bg=Colors.BG_HEADER)
        self.brand_frame.pack(side=LEFT)

        # 会社アイコン（工場マーク）
        self.icon_label = tk.Label(
            self.brand_frame,
            text="🏭",
            font=(Fonts.FAMILY, 24),
            bg=Colors.BG_HEADER
        )
        self.icon_label.pack(side=LEFT, padx=(0, Spacing.SM))

        # タイトルコンテナ
        self.title_container = tk.Frame(self.brand_frame, bg=Colors.BG_HEADER)
        self.title_container.pack(side=LEFT)

        # 会社名
        self.company_label = tk.Label(
            self.title_container,
            text="福井鐵工株式会社",
            font=(Fonts.FAMILY_DISPLAY, 11),
            fg=Colors.ACCENT_LIGHT,
            bg=Colors.BG_HEADER
        )
        self.company_label.pack(anchor=W)

        # アプリ名
        self.app_label = tk.Label(
            self.title_container,
            text="損益計算書 BI ツール",
            font=(Fonts.FAMILY_DISPLAY, Fonts.SIZE_HEADING, 'bold'),
            fg=Colors.WHITE,
            bg=Colors.BG_HEADER
        )
        self.app_label.pack(anchor=W)

        # 右側: 操作パネル
        self.control_frame = tk.Frame(header_inner, bg=Colors.BG_HEADER)
        self.control_frame.pack(side=RIGHT)

        # 期間選択ラベル
        self.period_label = tk.Label(
            self.control_frame,
            text="📅 対象期間",
            font=(Fonts.FAMILY, Fonts.SIZE_SMALL),
            fg=Colors.GRAY_300,
            bg=Colors.BG_HEADER
        )
        self.period_label.pack(side=LEFT, padx=(0, 6))

        # 期間コンボボックス
        self.period_var = ttk.StringVar()
        self.period_combo = ttk.Combobox(
            self.control_frame,
            textvariable=self.period_var,
            width=10,
            state="readonly",
            font=(Fonts.FAMILY, Fonts.SIZE_BODY)
        )
        self.period_combo.pack(side=LEFT, padx=(0, Spacing.SM))
        self.period_combo.bind("<<ComboboxSelected>>", self._on_period_change)

        # 更新ボタン
        self.refresh_btn = ttk.Button(
            self.control_frame,
            text="🔄 更新",
            command=self._refresh_data,
            bootstyle="warning",
            width=8
        )
        self.refresh_btn.pack(side=LEFT)

        # ヘッダーのレスポンシブ対応
        self._header_resize_job = None
        self._header_last_width = None
        self.header.bind('<Configure>', self._on_header_resize)

    def _on_header_resize(self, event):
        """ヘッダーリサイズ時の処理"""
        if event.width < 100:
            return

        if self._header_last_width == event.width:
            return

        self._header_last_width = event.width

        # 既存のジョブをキャンセル
        if self._header_resize_job:
            self.after_cancel(self._header_resize_job)

        # 100ms後にレイアウト調整
        self._header_resize_job = self.after(100, lambda: self._adjust_header_layout(event.width))

    def _adjust_header_layout(self, width: int):
        """ヘッダーレイアウトを調整"""
        # 幅に応じてフォントサイズとコンテンツを調整
        if width < 900:
            # 狭い場合：コンパクト表示
            self.icon_label.configure(font=(Fonts.FAMILY, 18))
            self.company_label.configure(font=(Fonts.FAMILY_DISPLAY, 9))
            self.app_label.configure(font=(Fonts.FAMILY_DISPLAY, 12, 'bold'))
            self.period_label.pack_forget()  # ラベルを非表示
            self.refresh_btn.configure(text="🔄", width=3)
        elif width < 1100:
            # 中間サイズ
            self.icon_label.configure(font=(Fonts.FAMILY, 20))
            self.company_label.configure(font=(Fonts.FAMILY_DISPLAY, 10))
            self.app_label.configure(font=(Fonts.FAMILY_DISPLAY, 13, 'bold'))
            self.period_label.pack(side=LEFT, padx=(0, 6), before=self.period_combo)
            self.refresh_btn.configure(text="🔄 更新", width=8)
        else:
            # 広い場合：フル表示
            self.icon_label.configure(font=(Fonts.FAMILY, 24))
            self.company_label.configure(font=(Fonts.FAMILY_DISPLAY, 11))
            self.app_label.configure(font=(Fonts.FAMILY_DISPLAY, Fonts.SIZE_HEADING, 'bold'))
            self.period_label.pack(side=LEFT, padx=(0, 6), before=self.period_combo)
            self.refresh_btn.configure(text="🔄 データ更新", width=12)

    def _create_notebook(self):
        """タブ付きノートブックを作成"""
        # ノートブックコンテナ
        notebook_container = ttk.Frame(self)
        notebook_container.pack(fill=BOTH, expand=True, padx=12, pady=(8, 0))

        self.notebook = ttk.Notebook(notebook_container, bootstyle="primary")
        self.notebook.pack(fill=BOTH, expand=True)

        # タブアイコン付きテキスト
        tab_configs = [
            ("📊  全社サマリー", DashboardView, {'processor': self.processor}),
            ("🏢  部門別分析", DepartmentView, {'processor': self.processor, 'loader': self.loader}),
            ("💹  原価分析", CostAnalysisView, {'processor': self.processor}),
            ("📋  詳細データ", DetailView, {'processor': self.processor, 'loader': self.loader}),
            ("📖  ガイド", GuideView, {}),
        ]

        self.views = {}
        for tab_text, ViewClass, kwargs in tab_configs:
            view = ViewClass(self.notebook, **kwargs)
            self.notebook.add(view, text=tab_text, padding=5)

            # ビュー参照を保存
            view_name = ViewClass.__name__.lower().replace('view', '')
            self.views[view_name] = view

        # 互換性のため個別参照も維持
        self.dashboard = self.views.get('dashboard')
        self.department_view = self.views.get('department')
        self.cost_view = self.views.get('costanalysis')
        self.detail_view = self.views.get('detail')
        self.guide_view = self.views.get('guide')

    def _create_statusbar(self):
        """ステータスバーを作成"""
        # ステータスバーコンテナ
        self.statusbar = tk.Frame(self, bg=Colors.GRAY_100, height=32)
        self.statusbar.pack(fill=X, side=BOTTOM)
        self.statusbar.pack_propagate(False)

        # 左側: データ読み込み状況
        loaded_files = self.loader.loaded_files
        file_count = len(loaded_files)

        status_left = tk.Frame(self.statusbar, bg=Colors.GRAY_100)
        status_left.pack(side=LEFT, padx=12, pady=6)

        # ステータスアイコン
        status_icon = tk.Label(
            status_left,
            text="✓" if file_count > 0 else "⚠",
            font=(Fonts.FAMILY, Fonts.SIZE_SMALL),
            fg=Colors.SUCCESS if file_count > 0 else Colors.WARNING,
            bg=Colors.GRAY_100
        )
        status_icon.pack(side=LEFT)

        self.status_label = tk.Label(
            status_left,
            text=f"読み込みファイル: {file_count}件",
            font=(Fonts.FAMILY, Fonts.SIZE_SMALL),
            fg=Colors.GRAY_600,
            bg=Colors.GRAY_100
        )
        self.status_label.pack(side=LEFT, padx=(6, 0))

        # 右側: 更新時刻
        status_right = tk.Frame(self.statusbar, bg=Colors.GRAY_100)
        status_right.pack(side=RIGHT, padx=12, pady=6)

        self.time_label = tk.Label(
            status_right,
            text=f"🕐 最終更新: {datetime.now().strftime('%Y/%m/%d %H:%M')}",
            font=(Fonts.FAMILY, Fonts.SIZE_SMALL),
            fg=Colors.GRAY_500,
            bg=Colors.GRAY_100
        )
        self.time_label.pack(side=RIGHT)

        # 中央: バージョン情報
        version_label = tk.Label(
            self.statusbar,
            text="Version 1.0",
            font=(Fonts.FAMILY, Fonts.SIZE_TINY),
            fg=Colors.GRAY_400,
            bg=Colors.GRAY_100
        )
        version_label.pack(pady=8)

    def _update_period_combo(self):
        """期間コンボボックスを更新"""
        periods = self.loader.get_periods()

        if periods:
            values = ["全期間"] + periods
            self.period_combo["values"] = values
            self.period_var.set("全期間")
        else:
            self.period_combo["values"] = ["データなし"]
            self.period_var.set("データなし")

    def _on_period_change(self, event):
        """期間変更時のコールバック"""
        selected = self.period_var.get()
        year_month = None if selected == "全期間" else selected

        # 全タブを更新
        if self.dashboard:
            self.dashboard.refresh(year_month)
        if self.department_view:
            self.department_view.refresh(year_month)
        if self.cost_view:
            self.cost_view.refresh(year_month)
        if self.detail_view:
            self.detail_view.refresh(year_month)

    def _refresh_data(self):
        """データを再読み込みして更新"""
        self.loader.reload()
        self.processor = DataProcessor(self.loader.df)

        # 全タブのprocessorを更新
        if self.dashboard:
            self.dashboard.processor = self.processor
        if self.department_view:
            self.department_view.processor = self.processor
        if self.cost_view:
            self.cost_view.processor = self.processor
        if self.detail_view:
            self.detail_view.processor = self.processor

        self._update_period_combo()

        selected = self.period_var.get()
        year_month = None if selected in ["全期間", "データなし"] else selected

        # 全タブを更新
        if self.dashboard:
            self.dashboard.refresh(year_month)
        if self.department_view:
            self.department_view.refresh(year_month)
        if self.cost_view:
            self.cost_view.refresh(year_month)
        if self.detail_view:
            self.detail_view.refresh(year_month)

        # ステータス更新
        file_count = len(self.loader.loaded_files)
        status_icon = "✓" if file_count > 0 else "⚠"
        self.status_label.configure(text=f"読み込みファイル: {file_count}件")
        self.time_label.configure(
            text=f"🕐 最終更新: {datetime.now().strftime('%Y/%m/%d %H:%M')}"
        )

    def run(self):
        """アプリケーションを実行"""
        self.mainloop()
