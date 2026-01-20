"""デザインテーマ設定 - 福井鐵工 損益計算書BIツール"""
import platform


# =============================================================================
# カラーパレット - 洗練されたビジネステーマ
# =============================================================================

class Colors:
    """アプリケーション全体のカラー定義"""

    # プライマリカラー（深いネイビー系）
    PRIMARY = '#1e3a5f'
    PRIMARY_LIGHT = '#2d5a87'
    PRIMARY_DARK = '#0f2744'

    # アクセントカラー（ゴールド系 - 福井鐵工のブランドイメージ）
    ACCENT = '#c9a227'
    ACCENT_LIGHT = '#e6c555'
    ACCENT_DARK = '#9a7b1a'

    # セマンティックカラー
    SUCCESS = '#0d9488'      # ティール（利益）
    SUCCESS_LIGHT = '#14b8a6'
    WARNING = '#d97706'      # オレンジ（注意）
    WARNING_LIGHT = '#f59e0b'
    DANGER = '#dc2626'       # 赤（損失・警告）
    DANGER_LIGHT = '#ef4444'
    INFO = '#0284c7'         # スカイブルー（情報）
    INFO_LIGHT = '#0ea5e9'

    # 中立色（グレースケール）
    WHITE = '#ffffff'
    GRAY_50 = '#f9fafb'
    GRAY_100 = '#f3f4f6'
    GRAY_200 = '#e5e7eb'
    GRAY_300 = '#d1d5db'
    GRAY_400 = '#9ca3af'
    GRAY_500 = '#6b7280'
    GRAY_600 = '#4b5563'
    GRAY_700 = '#374151'
    GRAY_800 = '#1f2937'
    GRAY_900 = '#111827'
    BLACK = '#000000'

    # 背景色
    BG_MAIN = '#f8fafc'         # メイン背景（淡いグレー）
    BG_CARD = '#ffffff'         # カード背景
    BG_SECTION = '#f1f5f9'      # セクション背景
    BG_HEADER = '#1e3a5f'       # ヘッダー背景（プライマリ）

    # ボーダー
    BORDER_LIGHT = '#e2e8f0'
    BORDER_DEFAULT = '#cbd5e1'
    BORDER_DARK = '#94a3b8'


# =============================================================================
# KPIカード用カラー（グラデーション風の組み合わせ）
# =============================================================================

class KPIColors:
    """KPIカード専用のカラー設定"""

    # 各KPI指標のカラーセット（背景, テキスト, アクセント）
    REVENUE = {
        'bg': '#dbeafe',          # 薄い青
        'bg_dark': '#bfdbfe',
        'text': '#1e40af',        # 濃い青
        'accent': '#3b82f6',
        'icon': '📊'
    }

    GROSS_PROFIT = {
        'bg': '#d1fae5',          # 薄い緑
        'bg_dark': '#a7f3d0',
        'text': '#065f46',        # 濃い緑
        'accent': '#10b981',
        'icon': '📈'
    }

    OPERATING_INCOME = {
        'bg': '#fef3c7',          # 薄いオレンジ
        'bg_dark': '#fde68a',
        'text': '#92400e',        # 濃いオレンジ
        'accent': '#f59e0b',
        'icon': '💰'
    }

    ORDINARY_INCOME = {
        'bg': '#ede9fe',          # 薄い紫
        'bg_dark': '#ddd6fe',
        'text': '#5b21b6',        # 濃い紫
        'accent': '#8b5cf6',
        'icon': '🎯'
    }


# =============================================================================
# グラフ用カラーパレット
# =============================================================================

class ChartColors:
    """グラフ用のカラー設定"""

    # メインのカラーパレット（8色）
    PALETTE = [
        '#3b82f6',  # 青
        '#10b981',  # 緑
        '#f59e0b',  # オレンジ
        '#ef4444',  # 赤
        '#8b5cf6',  # 紫
        '#06b6d4',  # シアン
        '#ec4899',  # ピンク
        '#84cc16',  # ライム
    ]

    # 原価分析用
    COST = {
        'material': '#ef4444',    # 材料費 - 赤
        'labor': '#3b82f6',       # 労務費 - 青
        'expense': '#10b981',     # 経費 - 緑
    }

    # 利益分析用
    PROFIT = {
        'gross': '#10b981',       # 売上総利益
        'operating': '#f59e0b',   # 営業利益
        'ordinary': '#8b5cf6',    # 経常利益
    }

    # ポジティブ/ネガティブ
    POSITIVE = '#10b981'
    NEGATIVE = '#ef4444'

    # グリッドとラベル
    GRID = '#e5e7eb'
    AXIS = '#9ca3af'
    LABEL = '#374151'


# =============================================================================
# フォント設定
# =============================================================================

class Fonts:
    """フォント設定"""

    # プラットフォームに応じた日本語フォント
    if platform.system() == 'Windows':
        FAMILY = 'Yu Gothic UI'
        FAMILY_BOLD = 'Yu Gothic UI'
        FAMILY_DISPLAY = 'Meiryo UI'
    elif platform.system() == 'Darwin':  # macOS
        FAMILY = 'Hiragino Sans'
        FAMILY_BOLD = 'Hiragino Sans'
        FAMILY_DISPLAY = 'Hiragino Sans'
    else:  # Linux
        FAMILY = 'Noto Sans CJK JP'
        FAMILY_BOLD = 'Noto Sans CJK JP'
        FAMILY_DISPLAY = 'Noto Sans CJK JP'

    # サイズ定義
    SIZE_TITLE = 18       # メインタイトル
    SIZE_HEADING = 14     # セクションタイトル
    SIZE_SUBHEADING = 12  # サブタイトル
    SIZE_BODY = 10        # 本文
    SIZE_SMALL = 9        # 補足テキスト
    SIZE_TINY = 8         # 非常に小さいテキスト

    # KPIカード用
    SIZE_KPI_VALUE = 22   # KPI値
    SIZE_KPI_TITLE = 11   # KPIタイトル
    SIZE_KPI_RATE = 10    # KPI率


# =============================================================================
# スペーシング定義
# =============================================================================

class Spacing:
    """余白とパディングの定義"""

    # 基本単位
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 20
    XXL = 24

    # セクション間
    SECTION_GAP = 16

    # カード内パディング
    CARD_PADDING = 16

    # コンテンツのマージン
    CONTENT_MARGIN = 20


# =============================================================================
# ボーダー・シャドウ定義
# =============================================================================

class Borders:
    """ボーダー設定"""

    RADIUS_SM = 4
    RADIUS_MD = 8
    RADIUS_LG = 12

    WIDTH_THIN = 1
    WIDTH_NORMAL = 2
    WIDTH_THICK = 3


# =============================================================================
# ttkbootstrap スタイル名マッピング
# =============================================================================

class Styles:
    """ttkbootstrap スタイル名"""

    # ボタン
    BTN_PRIMARY = 'primary'
    BTN_SUCCESS = 'success'
    BTN_WARNING = 'warning'
    BTN_DANGER = 'danger'
    BTN_INFO = 'info'
    BTN_OUTLINE_PRIMARY = 'outline-primary'
    BTN_OUTLINE_SUCCESS = 'outline-success'

    # テキスト
    TEXT_PRIMARY = 'primary'
    TEXT_SUCCESS = 'success'
    TEXT_WARNING = 'warning'
    TEXT_DANGER = 'danger'
    TEXT_SECONDARY = 'secondary'
    TEXT_MUTED = 'secondary'


# =============================================================================
# ヘルパー関数
# =============================================================================

def get_value_color(value: float) -> str:
    """値に応じた色を返す（正=緑、負=赤）"""
    if value > 0:
        return Colors.SUCCESS
    elif value < 0:
        return Colors.DANGER
    return Colors.GRAY_500


def get_trend_color(current: float, previous: float) -> str:
    """トレンドに応じた色を返す"""
    if current > previous:
        return Colors.SUCCESS
    elif current < previous:
        return Colors.DANGER
    return Colors.GRAY_500


def get_rate_color(rate: float, threshold_low: float = 0, threshold_high: float = 10) -> str:
    """率に応じた色を返す"""
    if rate < threshold_low:
        return Colors.DANGER
    elif rate < threshold_high:
        return Colors.WARNING
    return Colors.SUCCESS
