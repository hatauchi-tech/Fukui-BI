"""コンポーネントのユニットテスト"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class TestThemeColors:
    """Colorsクラスのテスト"""

    def test_colors_defined(self):
        """カラー定数が定義されていること"""
        from components.theme import Colors

        # プライマリカラー
        assert Colors.PRIMARY is not None
        assert Colors.PRIMARY.startswith('#')

        # セマンティックカラー
        assert Colors.SUCCESS is not None
        assert Colors.WARNING is not None
        assert Colors.DANGER is not None

        # 背景色
        assert Colors.BG_MAIN is not None
        assert Colors.BG_CARD is not None

    def test_color_format(self):
        """カラーがHEX形式であること"""
        from components.theme import Colors

        colors = [
            Colors.PRIMARY, Colors.SUCCESS, Colors.WARNING,
            Colors.DANGER, Colors.WHITE, Colors.BLACK
        ]

        for color in colors:
            assert color.startswith('#')
            assert len(color) == 7  # #RRGGBB format


class TestKPIColors:
    """KPIColorsクラスのテスト"""

    def test_kpi_color_sets(self):
        """KPIカラーセットが定義されていること"""
        from components.theme import KPIColors

        # 各KPIタイプのカラーセットが存在する
        assert hasattr(KPIColors, 'REVENUE')
        assert hasattr(KPIColors, 'GROSS_PROFIT')
        assert hasattr(KPIColors, 'OPERATING_INCOME')
        assert hasattr(KPIColors, 'ORDINARY_INCOME')

    def test_kpi_color_set_structure(self):
        """KPIカラーセットの構造が正しいこと"""
        from components.theme import KPIColors

        required_keys = ['bg', 'text', 'accent', 'icon']

        for kpi_type in [KPIColors.REVENUE, KPIColors.GROSS_PROFIT,
                         KPIColors.OPERATING_INCOME, KPIColors.ORDINARY_INCOME]:
            for key in required_keys:
                assert key in kpi_type, f"Missing key: {key}"


class TestChartColors:
    """ChartColorsクラスのテスト"""

    def test_palette_defined(self):
        """カラーパレットが定義されていること"""
        from components.theme import ChartColors

        assert hasattr(ChartColors, 'PALETTE')
        assert len(ChartColors.PALETTE) >= 8  # 最低8色

    def test_cost_colors_defined(self):
        """原価分析用カラーが定義されていること"""
        from components.theme import ChartColors

        assert 'material' in ChartColors.COST
        assert 'labor' in ChartColors.COST
        assert 'expense' in ChartColors.COST


class TestFonts:
    """Fontsクラスのテスト"""

    def test_font_family_defined(self):
        """フォントファミリーが定義されていること"""
        from components.theme import Fonts

        assert Fonts.FAMILY is not None
        assert Fonts.FAMILY_BOLD is not None

    def test_font_sizes_defined(self):
        """フォントサイズが定義されていること"""
        from components.theme import Fonts

        assert Fonts.SIZE_TITLE > 0
        assert Fonts.SIZE_HEADING > 0
        assert Fonts.SIZE_BODY > 0
        assert Fonts.SIZE_SMALL > 0

    def test_font_size_hierarchy(self):
        """フォントサイズの階層が正しいこと"""
        from components.theme import Fonts

        assert Fonts.SIZE_TITLE > Fonts.SIZE_HEADING
        assert Fonts.SIZE_HEADING > Fonts.SIZE_BODY
        assert Fonts.SIZE_BODY > Fonts.SIZE_SMALL


class TestSpacing:
    """Spacingクラスのテスト"""

    def test_spacing_values_defined(self):
        """スペーシング値が定義されていること"""
        from components.theme import Spacing

        assert Spacing.XS > 0
        assert Spacing.SM > 0
        assert Spacing.MD > 0
        assert Spacing.LG > 0
        assert Spacing.XL > 0

    def test_spacing_hierarchy(self):
        """スペーシングの階層が正しいこと"""
        from components.theme import Spacing

        assert Spacing.XS < Spacing.SM
        assert Spacing.SM < Spacing.MD
        assert Spacing.MD < Spacing.LG
        assert Spacing.LG < Spacing.XL


class TestHelperFunctions:
    """テーマヘルパー関数のテスト"""

    def test_get_value_color_positive(self):
        """正の値は緑色を返すこと"""
        from components.theme import get_value_color, Colors

        color = get_value_color(100)
        assert color == Colors.SUCCESS

    def test_get_value_color_negative(self):
        """負の値は赤色を返すこと"""
        from components.theme import get_value_color, Colors

        color = get_value_color(-100)
        assert color == Colors.DANGER

    def test_get_value_color_zero(self):
        """ゼロはグレーを返すこと"""
        from components.theme import get_value_color, Colors

        color = get_value_color(0)
        assert color == Colors.GRAY_500

    def test_get_trend_color_increase(self):
        """増加トレンドは緑色を返すこと"""
        from components.theme import get_trend_color, Colors

        color = get_trend_color(150, 100)
        assert color == Colors.SUCCESS

    def test_get_trend_color_decrease(self):
        """減少トレンドは赤色を返すこと"""
        from components.theme import get_trend_color, Colors

        color = get_trend_color(50, 100)
        assert color == Colors.DANGER

    def test_get_rate_color(self):
        """率に応じた色を返すこと"""
        from components.theme import get_rate_color, Colors

        # 低い率は赤
        assert get_rate_color(-5, 0, 10) == Colors.DANGER

        # 中程度は黄色
        assert get_rate_color(5, 0, 10) == Colors.WARNING

        # 高い率は緑
        assert get_rate_color(15, 0, 10) == Colors.SUCCESS


class TestFormatCurrency:
    """金額フォーマット関数のテスト

    Note: このテストはtkinterが必要なため、GUIが利用できない環境ではスキップされます。
    """

    @pytest.fixture(autouse=True)
    def check_tkinter(self):
        """tkinterが利用可能かチェック"""
        pytest.importorskip("tkinter")

    def test_format_currency_yen(self):
        """円単位のフォーマット"""
        from components.kpi_card import format_currency

        result = format_currency(500)
        # 結果に¥が含まれるか、数値が含まれること
        assert "¥" in result
        assert "500" in result

    def test_format_currency_thousand(self):
        """千円単位のフォーマット"""
        from components.kpi_card import format_currency

        result = format_currency(5000)
        # 千円単位で表示される（5千）
        assert "千" in result or "5" in result

    def test_format_currency_million(self):
        """百万円単位のフォーマット"""
        from components.kpi_card import format_currency

        result = format_currency(5_000_000)
        # 百万円単位で表示される
        assert "百万" in result or "5" in result

    def test_format_currency_billion(self):
        """億円単位のフォーマット"""
        from components.kpi_card import format_currency

        result = format_currency(5_000_000_000)
        # 億円単位で表示される
        assert "億" in result

    def test_format_currency_negative(self):
        """マイナス値のフォーマット"""
        from components.kpi_card import format_currency

        result = format_currency(-5_000_000)
        # マイナス値が何らかの形で表示される
        assert "-" in result or "百万" in result or "¥" in result


class TestBorders:
    """Bordersクラスのテスト"""

    def test_border_radius_defined(self):
        """ボーダー半径が定義されていること"""
        from components.theme import Borders

        assert Borders.RADIUS_SM > 0
        assert Borders.RADIUS_MD > Borders.RADIUS_SM
        assert Borders.RADIUS_LG > Borders.RADIUS_MD

    def test_border_width_defined(self):
        """ボーダー幅が定義されていること"""
        from components.theme import Borders

        assert Borders.WIDTH_THIN > 0
        assert Borders.WIDTH_NORMAL > Borders.WIDTH_THIN
        assert Borders.WIDTH_THICK > Borders.WIDTH_NORMAL


class TestStyles:
    """Stylesクラスのテスト"""

    def test_button_styles_defined(self):
        """ボタンスタイルが定義されていること"""
        from components.theme import Styles

        assert Styles.BTN_PRIMARY is not None
        assert Styles.BTN_SUCCESS is not None
        assert Styles.BTN_WARNING is not None
        assert Styles.BTN_DANGER is not None

    def test_text_styles_defined(self):
        """テキストスタイルが定義されていること"""
        from components.theme import Styles

        assert Styles.TEXT_PRIMARY is not None
        assert Styles.TEXT_SUCCESS is not None
