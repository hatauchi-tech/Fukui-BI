"""グラフコンポーネント - レスポンシブ対応版"""
import platform
import tkinter as tk
from typing import Optional
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

from .theme import ChartColors, Colors, Fonts

# =============================================================================
# Matplotlib 設定
# =============================================================================

if platform.system() == 'Windows':
    plt.rcParams['font.family'] = ['Yu Gothic UI', 'Yu Gothic', 'MS Gothic', 'Meiryo', 'sans-serif']
elif platform.system() == 'Darwin':
    plt.rcParams['font.family'] = ['Hiragino Sans', 'Hiragino Kaku Gothic ProN', 'sans-serif']
else:
    plt.rcParams['font.family'] = ['Noto Sans CJK JP', 'IPAGothic', 'sans-serif']

plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.autolayout'] = False
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.labelcolor'] = ChartColors.LABEL
plt.rcParams['xtick.color'] = ChartColors.LABEL
plt.rcParams['ytick.color'] = ChartColors.LABEL


class ChartFrame(tk.Frame):
    """グラフ表示用フレーム（レスポンシブ対応）"""

    # 最小サイズ
    MIN_WIDTH = 200
    MIN_HEIGHT = 150

    def __init__(self, parent, figsize=(6, 4), **kwargs):
        super().__init__(parent, bg=Colors.WHITE, **kwargs)

        self.base_figsize = figsize
        self.figure = Figure(figsize=figsize, dpi=100, facecolor=Colors.WHITE)
        self.canvas = FigureCanvasTkAgg(self.figure, self)

        # キャンバスウィジェットを配置
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        # リサイズ対応
        self._resize_job = None
        self._last_size = None
        self._plot_data = None  # 再描画用にデータを保持
        self._plot_type = None
        self._plot_kwargs = {}

        self.bind('<Configure>', self._on_resize)

    def _on_resize(self, event):
        """リサイズイベント処理（デバウンス付き）"""
        new_size = (event.width, event.height)

        # 最小サイズ未満は無視
        if event.width < self.MIN_WIDTH or event.height < self.MIN_HEIGHT:
            return

        # サイズが変わっていない場合は無視
        if self._last_size == new_size:
            return

        self._last_size = new_size

        # 既存のジョブをキャンセル
        if self._resize_job:
            self.after_cancel(self._resize_job)

        # 150ms後にリサイズ処理を実行（デバウンス）
        self._resize_job = self.after(150, self._do_resize)

    def _do_resize(self):
        """実際のリサイズ処理"""
        if self._last_size is None:
            return

        width, height = self._last_size

        # DPIを考慮したサイズ計算
        dpi = self.figure.get_dpi()
        new_width = max(width / dpi, 2)
        new_height = max(height / dpi, 1.5)

        # Figureサイズを更新
        self.figure.set_size_inches(new_width, new_height, forward=True)

        # データがあれば再描画
        if self._plot_data is not None and self._plot_type:
            self._replot()

    def _replot(self):
        """保存されたデータで再描画"""
        pass  # サブクラスでオーバーライド

    def clear(self):
        """グラフをクリア"""
        self.figure.clear()
        self._plot_data = None
        self._plot_type = None

    def draw(self):
        """グラフを描画"""
        self.canvas.draw_idle()

    def _truncate_label(self, label: str, max_length: int = 8) -> str:
        """ラベルを省略"""
        if len(label) > max_length:
            return label[:max_length-1] + '…'
        return label

    def _get_font_size(self, base_size: int = 9) -> int:
        """ウィジェットサイズに応じたフォントサイズを返す"""
        if self._last_size:
            width = self._last_size[0]
            if width < 300:
                return max(base_size - 2, 7)
            elif width < 400:
                return max(base_size - 1, 8)
        return base_size

    def _style_axis(self, ax):
        """軸のスタイリングを共通化"""
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(ChartColors.GRID)
        ax.spines['bottom'].set_color(ChartColors.GRID)
        font_size = self._get_font_size(9)
        ax.tick_params(colors=ChartColors.LABEL, labelsize=font_size)
        ax.set_facecolor(Colors.WHITE)

    def _get_margins(self, chart_type: str = 'bar') -> dict:
        """チャートタイプとサイズに応じたマージンを返す"""
        if self._last_size:
            width = self._last_size[0]
            if width < 350:
                if chart_type == 'pie':
                    return {'left': 0.02, 'right': 0.65, 'top': 0.90, 'bottom': 0.05}
                elif chart_type == 'bar_h':
                    return {'left': 0.35, 'right': 0.95, 'top': 0.90, 'bottom': 0.10}
                else:
                    return {'left': 0.18, 'right': 0.95, 'top': 0.90, 'bottom': 0.25}

        # デフォルト
        if chart_type == 'pie':
            return {'left': 0.05, 'right': 0.72, 'top': 0.88, 'bottom': 0.08}
        elif chart_type == 'bar_h':
            return {'left': 0.28, 'right': 0.95, 'top': 0.88, 'bottom': 0.12}
        else:
            return {'left': 0.15, 'right': 0.95, 'top': 0.88, 'bottom': 0.22}


class BarChart(ChartFrame):
    """棒グラフ（レスポンシブ対応）"""

    def plot(
        self,
        labels: list[str],
        values: list[float],
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        color: str = None,
        horizontal: bool = False
    ):
        """棒グラフを描画"""
        # データを保存
        self._plot_data = {
            'labels': labels,
            'values': values,
            'title': title,
            'xlabel': xlabel,
            'ylabel': ylabel,
            'color': color,
            'horizontal': horizontal
        }
        self._plot_type = 'bar'

        self._draw_bar(**self._plot_data)

    def _replot(self):
        """再描画"""
        if self._plot_data:
            self._draw_bar(**self._plot_data)

    def _draw_bar(self, labels, values, title, xlabel, ylabel, color, horizontal):
        """実際の描画処理"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if color is None:
            color = ChartColors.PALETTE[0]

        font_size = self._get_font_size(9)
        title_size = self._get_font_size(11)

        # ラベル省略文字数をサイズに応じて調整
        max_label_len = 6 if not horizontal else 12
        if self._last_size and self._last_size[0] < 350:
            max_label_len = 4 if not horizontal else 8

        display_labels = [self._truncate_label(l, max_label_len) for l in labels]
        colors = [color if v >= 0 else ChartColors.NEGATIVE for v in values]

        if horizontal:
            y_pos = np.arange(len(display_labels))
            ax.barh(y_pos, values, color=colors, height=0.6, edgecolor='none')
            ax.set_yticks(y_pos)
            ax.set_yticklabels(display_labels, fontsize=font_size)
            ax.set_xlabel(ylabel, fontsize=font_size)
            ax.invert_yaxis()
            ax.axvline(x=0, color=ChartColors.GRID, linewidth=1)
            ax.grid(axis='x', linestyle='-', alpha=0.3, color=ChartColors.GRID)
            margins = self._get_margins('bar_h')
        else:
            x_pos = np.arange(len(display_labels))
            ax.bar(x_pos, values, color=colors, width=0.6, edgecolor='none')
            ax.set_xticks(x_pos)
            ax.set_xticklabels(display_labels, fontsize=font_size, rotation=30, ha='right')
            ax.set_ylabel(ylabel, fontsize=font_size)
            ax.axhline(y=0, color=ChartColors.GRID, linewidth=1)
            ax.grid(axis='y', linestyle='-', alpha=0.3, color=ChartColors.GRID)
            margins = self._get_margins('bar')

        if title:
            ax.set_title(title, fontsize=title_size, fontweight='bold', pad=10, color=Colors.GRAY_800)

        self._style_axis(ax)
        self.figure.subplots_adjust(**margins)
        self.canvas.draw_idle()


class PieChart(ChartFrame):
    """円グラフ（レスポンシブ対応）"""

    def plot(
        self,
        labels: list[str],
        values: list[float],
        title: str = "",
        colors: Optional[list[str]] = None
    ):
        """円グラフを描画"""
        self._plot_data = {
            'labels': labels,
            'values': values,
            'title': title,
            'colors': colors
        }
        self._plot_type = 'pie'

        self._draw_pie(**self._plot_data)

    def _replot(self):
        if self._plot_data:
            self._draw_pie(**self._plot_data)

    def _draw_pie(self, labels, values, title, colors):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        positive_values = [max(0, v) for v in values]

        if sum(positive_values) == 0:
            ax.text(0.5, 0.5, 'データがありません',
                   ha='center', va='center',
                   transform=ax.transAxes, fontsize=11, color=Colors.GRAY_500)
            if title:
                ax.set_title(title, fontsize=11, fontweight='bold', pad=10, color=Colors.GRAY_800)
            self.canvas.draw_idle()
            return

        non_zero_mask = [v > 0 for v in positive_values]
        max_label_len = 8
        if self._last_size and self._last_size[0] < 350:
            max_label_len = 5

        filtered_labels = [self._truncate_label(l, max_label_len) for l, m in zip(labels, non_zero_mask) if m]
        filtered_values = [v for v, m in zip(positive_values, non_zero_mask) if m]

        if colors is None:
            plot_colors = ChartColors.PALETTE[:len(filtered_labels)]
        else:
            plot_colors = [c for c, m in zip(colors, non_zero_mask) if m]

        font_size = self._get_font_size(9)
        title_size = self._get_font_size(11)

        wedges, texts, autotexts = ax.pie(
            filtered_values,
            labels=None,
            autopct='%1.1f%%',
            colors=plot_colors,
            startangle=90,
            pctdistance=0.6,
            wedgeprops={'edgecolor': Colors.WHITE, 'linewidth': 2}
        )

        for autotext in autotexts:
            autotext.set_fontsize(font_size)
            autotext.set_fontweight('bold')
            autotext.set_color(Colors.WHITE)

        # 凡例の位置をサイズに応じて調整
        legend_anchor = (0.88, 0.5)
        if self._last_size and self._last_size[0] < 400:
            legend_anchor = (0.75, 0.5)

        ax.legend(
            wedges, filtered_labels,
            loc='center left',
            bbox_to_anchor=legend_anchor,
            fontsize=font_size,
            frameon=False
        )

        if title:
            ax.set_title(title, fontsize=title_size, fontweight='bold', pad=10, color=Colors.GRAY_800)

        ax.axis('equal')

        margins = self._get_margins('pie')
        self.figure.subplots_adjust(**margins)
        self.canvas.draw_idle()


class LineChart(ChartFrame):
    """折れ線グラフ（レスポンシブ対応）"""

    def plot(
        self,
        x_data: list,
        y_data_dict: dict[str, list[float]],
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        show_markers: bool = True
    ):
        self._plot_data = {
            'x_data': x_data,
            'y_data_dict': y_data_dict,
            'title': title,
            'xlabel': xlabel,
            'ylabel': ylabel,
            'show_markers': show_markers
        }
        self._plot_type = 'line'

        self._draw_line(**self._plot_data)

    def _replot(self):
        if self._plot_data:
            self._draw_line(**self._plot_data)

    def _draw_line(self, x_data, y_data_dict, title, xlabel, ylabel, show_markers):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        colors = ChartColors.PALETTE
        markers = ['o', 's', '^', 'D', 'v']

        font_size = self._get_font_size(9)
        title_size = self._get_font_size(11)

        max_label_len = 7
        if self._last_size and self._last_size[0] < 350:
            max_label_len = 4

        display_x = [self._truncate_label(str(x), max_label_len) for x in x_data]

        # マーカーサイズをウィンドウサイズに応じて調整
        marker_size = 6
        line_width = 2.5
        if self._last_size and self._last_size[0] < 400:
            marker_size = 4
            line_width = 2

        for i, (name, y_data) in enumerate(y_data_dict.items()):
            marker = markers[i % len(markers)] if show_markers else None
            ax.plot(
                range(len(x_data)),
                y_data,
                label=name,
                color=colors[i % len(colors)],
                marker=marker,
                markersize=marker_size,
                linewidth=line_width,
                markerfacecolor=Colors.WHITE,
                markeredgewidth=2
            )

        ax.set_xticks(range(len(display_x)))
        ax.set_xticklabels(display_x, fontsize=font_size, rotation=30, ha='right')

        if title:
            ax.set_title(title, fontsize=title_size, fontweight='bold', pad=10, color=Colors.GRAY_800)
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=font_size)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=font_size)

        ax.legend(loc='upper left', fontsize=font_size, frameon=True, fancybox=True, shadow=False)
        ax.grid(True, linestyle='-', alpha=0.3, color=ChartColors.GRID)
        ax.axhline(y=0, color=ChartColors.GRID, linewidth=1)

        self._style_axis(ax)

        margins = self._get_margins('line')
        self.figure.subplots_adjust(**margins)
        self.canvas.draw_idle()


class StackedBarChart(ChartFrame):
    """積み上げ棒グラフ（レスポンシブ対応）"""

    def plot(
        self,
        labels: list[str],
        data_dict: dict[str, list[float]],
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        colors: Optional[list[str]] = None
    ):
        self._plot_data = {
            'labels': labels,
            'data_dict': data_dict,
            'title': title,
            'xlabel': xlabel,
            'ylabel': ylabel,
            'colors': colors
        }
        self._plot_type = 'stacked'

        self._draw_stacked(**self._plot_data)

    def _replot(self):
        if self._plot_data:
            self._draw_stacked(**self._plot_data)

    def _draw_stacked(self, labels, data_dict, title, xlabel, ylabel, colors):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if colors is None:
            colors = ChartColors.PALETTE

        font_size = self._get_font_size(9)
        title_size = self._get_font_size(11)

        max_label_len = 6
        if self._last_size and self._last_size[0] < 350:
            max_label_len = 4

        display_labels = [self._truncate_label(l, max_label_len) for l in labels]
        x_pos = np.arange(len(display_labels))

        bottom = np.zeros(len(labels))

        for i, (name, values) in enumerate(data_dict.items()):
            values_arr = np.array(values)
            ax.bar(
                x_pos,
                values_arr,
                bottom=bottom,
                label=name,
                color=colors[i % len(colors)],
                width=0.6,
                edgecolor=Colors.WHITE,
                linewidth=0.5
            )
            bottom += values_arr

        ax.set_xticks(x_pos)
        ax.set_xticklabels(display_labels, fontsize=font_size, rotation=30, ha='right')

        if title:
            ax.set_title(title, fontsize=title_size, fontweight='bold', pad=10, color=Colors.GRAY_800)
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=font_size)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=font_size)

        ax.legend(loc='upper right', fontsize=font_size, frameon=True, fancybox=True)
        ax.grid(axis='y', linestyle='-', alpha=0.3, color=ChartColors.GRID)

        self._style_axis(ax)

        margins = self._get_margins('bar')
        self.figure.subplots_adjust(**margins)
        self.canvas.draw_idle()
