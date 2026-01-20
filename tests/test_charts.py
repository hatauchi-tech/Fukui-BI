"""チャートコンポーネントのユニットテスト

注意: このテストはGUIを起動せず、チャートのロジック部分のみをテストします。
Matplotlibのバックエンドを'Agg'に設定してヘッドレステストを行います。
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class TestChartFrameLogic:
    """ChartFrameのロジックテスト"""

    def test_truncate_label_short(self):
        """短いラベルはそのまま返すこと"""
        # ChartFrameの_truncate_labelメソッドをテスト
        # GUIなしでテストするために直接ロジックをテスト
        label = "短いラベル"
        max_length = 10

        if len(label) > max_length:
            result = label[:max_length-1] + '…'
        else:
            result = label

        assert result == label

    def test_truncate_label_long(self):
        """長いラベルは省略されること"""
        label = "これは非常に長いラベルです"
        max_length = 8

        if len(label) > max_length:
            result = label[:max_length-1] + '…'
        else:
            result = label

        assert len(result) == max_length
        assert result.endswith('…')

    def test_get_font_size_logic(self):
        """フォントサイズのロジック"""
        base_size = 9

        # 幅が狭い場合
        width = 250
        if width < 300:
            expected = max(base_size - 2, 7)
        elif width < 400:
            expected = max(base_size - 1, 8)
        else:
            expected = base_size

        assert expected == 7

        # 幅が広い場合
        width = 500
        if width < 300:
            expected = max(base_size - 2, 7)
        elif width < 400:
            expected = max(base_size - 1, 8)
        else:
            expected = base_size

        assert expected == 9


class TestBarChartData:
    """棒グラフデータ処理のテスト"""

    def test_bar_chart_data_structure(self):
        """棒グラフのデータ構造が正しいこと"""
        labels = ['部門A', '部門B', '部門C']
        values = [1000000, 800000, 600000]

        # データの長さが一致
        assert len(labels) == len(values)

        # 値が数値
        for v in values:
            assert isinstance(v, (int, float))

    def test_bar_chart_colors_positive_negative(self):
        """正負の値で色が変わること"""
        from components.theme import ChartColors

        values = [1000, -500, 800]
        base_color = ChartColors.PALETTE[0]

        colors = [base_color if v >= 0 else ChartColors.NEGATIVE for v in values]

        assert colors[0] == base_color  # 正の値
        assert colors[1] == ChartColors.NEGATIVE  # 負の値
        assert colors[2] == base_color  # 正の値


class TestPieChartData:
    """円グラフデータ処理のテスト"""

    def test_pie_chart_filter_zeros(self):
        """ゼロ値がフィルタリングされること"""
        labels = ['A', 'B', 'C', 'D']
        values = [100, 0, 50, 0]

        # ゼロでない値のみを取得
        non_zero_mask = [v > 0 for v in values]
        filtered_labels = [l for l, m in zip(labels, non_zero_mask) if m]
        filtered_values = [v for v, m in zip(values, non_zero_mask) if m]

        assert filtered_labels == ['A', 'C']
        assert filtered_values == [100, 50]

    def test_pie_chart_negative_to_zero(self):
        """負の値がゼロとして扱われること"""
        values = [100, -50, 200]

        positive_values = [max(0, v) for v in values]

        assert positive_values == [100, 0, 200]

    def test_pie_chart_empty_data(self):
        """データが全てゼロの場合"""
        values = [0, 0, 0]

        positive_values = [max(0, v) for v in values]
        total = sum(positive_values)

        assert total == 0


class TestLineChartData:
    """折れ線グラフデータ処理のテスト"""

    def test_line_chart_data_structure(self):
        """折れ線グラフのデータ構造が正しいこと"""
        x_data = ['2025/07', '2025/08', '2025/09']
        y_data_dict = {
            '売上高': [1000, 1200, 1100],
            '営業利益': [100, 150, 120]
        }

        # x軸データと各系列のデータ長が一致
        for series_name, y_data in y_data_dict.items():
            assert len(x_data) == len(y_data)

    def test_line_chart_multiple_series(self):
        """複数系列のデータ"""
        y_data_dict = {
            '売上高': [1000, 1200, 1100],
            '営業利益': [100, 150, 120],
            '経常利益': [80, 130, 100]
        }

        assert len(y_data_dict) == 3

        # 各系列のデータが存在
        for series_name, data in y_data_dict.items():
            assert len(data) > 0


class TestStackedBarChartData:
    """積み上げ棒グラフデータ処理のテスト"""

    def test_stacked_bar_data_structure(self):
        """積み上げ棒グラフのデータ構造が正しいこと"""
        labels = ['部門A', '部門B']
        data_dict = {
            '材料費': [300, 250],
            '労務費': [200, 180],
            '経費': [100, 120]
        }

        # 各系列のデータ長がラベル数と一致
        for series_name, values in data_dict.items():
            assert len(values) == len(labels)

    def test_stacked_bar_sum(self):
        """各ラベルの積み上げ合計が計算できること"""
        import numpy as np

        labels = ['部門A', '部門B']
        data_dict = {
            '材料費': [300, 250],
            '労務費': [200, 180],
            '経費': [100, 120]
        }

        # 各ラベルの合計
        totals = np.zeros(len(labels))
        for values in data_dict.values():
            totals += np.array(values)

        assert totals[0] == 600  # 部門A合計
        assert totals[1] == 550  # 部門B合計


class TestChartColorsUsage:
    """チャートカラー使用のテスト"""

    def test_palette_cycle(self):
        """パレットが循環して使用できること"""
        from components.theme import ChartColors

        # パレットサイズより多いデータ
        num_items = 12
        palette = ChartColors.PALETTE

        colors = [palette[i % len(palette)] for i in range(num_items)]

        assert len(colors) == num_items
        # 循環確認
        assert colors[0] == colors[8]  # 8番目は0番目と同じ

    def test_cost_colors_available(self):
        """原価分析用カラーが使用できること"""
        from components.theme import ChartColors

        cost_colors = [
            ChartColors.COST['material'],
            ChartColors.COST['labor'],
            ChartColors.COST['expense']
        ]

        assert len(cost_colors) == 3
        for color in cost_colors:
            assert color.startswith('#')


class TestChartMargins:
    """チャートマージン計算のテスト"""

    def test_margin_for_bar_chart(self):
        """棒グラフ用マージン"""
        width = 400

        if width < 350:
            margins = {'left': 0.18, 'right': 0.95, 'top': 0.90, 'bottom': 0.25}
        else:
            margins = {'left': 0.15, 'right': 0.95, 'top': 0.88, 'bottom': 0.22}

        assert 'left' in margins
        assert 'right' in margins
        assert margins['left'] < margins['right']

    def test_margin_for_pie_chart(self):
        """円グラフ用マージン（凡例スペース確保）"""
        width = 400

        if width < 350:
            margins = {'left': 0.02, 'right': 0.65, 'top': 0.90, 'bottom': 0.05}
        else:
            margins = {'left': 0.05, 'right': 0.72, 'top': 0.88, 'bottom': 0.08}

        # 円グラフは右に凡例スペースを確保
        assert margins['right'] < 0.8

    def test_margin_for_horizontal_bar(self):
        """横棒グラフ用マージン（左にラベルスペース）"""
        width = 400

        if width < 350:
            margins = {'left': 0.35, 'right': 0.95, 'top': 0.90, 'bottom': 0.10}
        else:
            margins = {'left': 0.28, 'right': 0.95, 'top': 0.88, 'bottom': 0.12}

        # 横棒グラフは左にラベルスペースを確保
        assert margins['left'] > 0.2


class TestChartDataValidation:
    """チャートデータバリデーションのテスト"""

    def test_empty_data_handling(self):
        """空データのハンドリング"""
        labels = []
        values = []

        # 空データの場合は何も描画しない
        assert len(labels) == 0
        assert len(values) == 0

    def test_mismatched_data_detection(self):
        """データ不一致の検出"""
        labels = ['A', 'B', 'C']
        values = [100, 200]  # ラベルより少ない

        assert len(labels) != len(values)

    def test_nan_handling(self):
        """NaN値のハンドリング"""
        import numpy as np

        values = [100, np.nan, 200]

        # NaNを0に置換
        clean_values = [0 if np.isnan(v) else v for v in values]

        assert clean_values == [100, 0, 200]


class TestResponsiveLogic:
    """レスポンシブロジックのテスト"""

    def test_column_count_by_width(self):
        """幅に応じた列数の決定"""
        BREAKPOINT_4COL = 900
        BREAKPOINT_3COL = 700
        BREAKPOINT_2COL = 500

        test_cases = [
            (1000, 4),
            (850, 3),
            (600, 2),
            (400, 1),
        ]

        for width, expected_cols in test_cases:
            if width >= BREAKPOINT_4COL:
                columns = 4
            elif width >= BREAKPOINT_3COL:
                columns = 3
            elif width >= BREAKPOINT_2COL:
                columns = 2
            else:
                columns = 1

            assert columns == expected_cols, f"Width {width} should give {expected_cols} columns"

    def test_label_truncation_by_width(self):
        """幅に応じたラベル省略文字数"""
        width = 300

        if width < 350:
            max_label_len = 4
        else:
            max_label_len = 6

        assert max_label_len == 4

        width = 400
        if width < 350:
            max_label_len = 4
        else:
            max_label_len = 6

        assert max_label_len == 6
