"""DataLoader のユニットテスト"""
import os
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from data_loader import DataLoader


class TestDataLoaderInit:
    """DataLoader 初期化のテスト"""

    def test_init_default_folder(self):
        """デフォルトのデータフォルダで初期化できること"""
        loader = DataLoader()
        assert loader.data_folder.name == "損益計算書"

    def test_init_custom_folder(self, tmp_path):
        """カスタムフォルダで初期化できること"""
        custom_folder = tmp_path / "custom_data"
        custom_folder.mkdir()
        loader = DataLoader(data_folder=str(custom_folder))
        # base_pathからの相対パスではなく、絶対パスを確認
        assert loader.data_folder.name == "custom_data"


class TestExtractYearMonth:
    """ファイル名から年月抽出のテスト"""

    def test_extract_standard_format(self):
        """標準的なファイル名から年月を抽出できること"""
        loader = DataLoader()
        result = loader._extract_year_month_from_filename("2025_07_損益計算書.csv")
        assert result == "2025/07"

    def test_extract_different_year(self):
        """異なる年のファイル名から年月を抽出できること"""
        loader = DataLoader()
        result = loader._extract_year_month_from_filename("2024_12_損益計算書.csv")
        assert result == "2024/12"

    def test_extract_invalid_format(self):
        """無効なフォーマットではNoneを返すこと"""
        loader = DataLoader()
        result = loader._extract_year_month_from_filename("invalid_filename.csv")
        assert result is None

    def test_extract_partial_match(self):
        """パターンに部分一致してもマッチすること"""
        loader = DataLoader()
        result = loader._extract_year_month_from_filename("prefix_2025_08_suffix.csv")
        assert result == "2025/08"


class TestLoadFile:
    """単一ファイル読み込みのテスト"""

    def test_load_valid_csv(self, test_loader, temp_data_folder):
        """有効なCSVファイルを読み込めること"""
        csv_path = temp_data_folder / "2025_07_損益計算書.csv"
        df = test_loader.load_file(csv_path)

        assert not df.empty
        assert 'source_file' in df.columns
        assert 'year_month' in df.columns
        assert df['year_month'].iloc[0] == "2025/07"

    def test_load_file_has_correct_columns(self, test_loader, temp_data_folder):
        """読み込んだファイルに必要なカラムがあること"""
        csv_path = temp_data_folder / "2025_07_損益計算書.csv"
        df = test_loader.load_file(csv_path)

        required_columns = ['部課ｺｰﾄﾞ', '部課名', '科目ｺｰﾄﾞ', '科目名', '残高', '出力帳票']
        for col in required_columns:
            assert col in df.columns, f"Missing column: {col}"

    def test_numeric_columns_converted(self, test_loader, temp_data_folder):
        """数値カラムが正しく変換されること"""
        csv_path = temp_data_folder / "2025_07_損益計算書.csv"
        df = test_loader.load_file(csv_path)

        for col in ['前残高', '借方', '貸方', '残高']:
            assert df[col].dtype in ['float64', 'int64'], f"{col} should be numeric"


class TestLoadAll:
    """全ファイル読み込みのテスト"""

    def test_load_all_files(self, test_loader):
        """全CSVファイルを読み込めること"""
        df = test_loader.load_all()

        assert not df.empty
        # 7月と8月の両方が含まれる
        assert '2025/07' in df['year_month'].values
        assert '2025/08' in df['year_month'].values

    def test_load_empty_folder(self, empty_test_loader):
        """空のフォルダから読み込むと空のDataFrameを返すこと"""
        df = empty_test_loader.load_all()

        assert df.empty

    def test_loaded_files_tracked(self, test_loader):
        """読み込んだファイルが追跡されること"""
        test_loader.load_all()

        assert len(test_loader.loaded_files) == 2
        assert "2025_07_損益計算書.csv" in test_loader.loaded_files
        assert "2025_08_損益計算書.csv" in test_loader.loaded_files


class TestReload:
    """データ再読み込みのテスト"""

    def test_reload_clears_and_reloads(self, test_loader):
        """reloadでデータがクリアされて再読み込みされること"""
        # 初回読み込み
        test_loader.load_all()
        initial_files = test_loader.loaded_files.copy()

        # 再読み込み
        test_loader.reload()

        assert test_loader.loaded_files == initial_files


class TestGetDepartments:
    """部門一覧取得のテスト"""

    def test_get_departments(self, test_loader):
        """部門一覧を取得できること"""
        departments = test_loader.get_departments()

        assert len(departments) >= 2
        dept_codes = [code for code, _ in departments]
        assert 210 in dept_codes  # 建機事業部
        assert 220 in dept_codes  # 社会インフラ製作

    def test_get_departments_sorted(self, test_loader):
        """部門一覧がコード順にソートされていること"""
        departments = test_loader.get_departments()
        dept_codes = [code for code, _ in departments]

        assert dept_codes == sorted(dept_codes)


class TestGetPeriods:
    """期間一覧取得のテスト"""

    def test_get_periods(self, test_loader):
        """期間一覧を取得できること"""
        periods = test_loader.get_periods()

        assert len(periods) == 2
        assert '2025/07' in periods
        assert '2025/08' in periods

    def test_get_periods_sorted(self, test_loader):
        """期間一覧がソートされていること"""
        periods = test_loader.get_periods()

        assert periods == sorted(periods)


class TestGetLatestPeriod:
    """最新期間取得のテスト"""

    def test_get_latest_period(self, test_loader):
        """最新の期間を取得できること"""
        latest = test_loader.get_latest_period()

        assert latest == '2025/08'

    def test_get_latest_period_empty(self, empty_test_loader):
        """空の場合はNoneを返すこと"""
        latest = empty_test_loader.get_latest_period()

        assert latest is None


class TestDataFrameProperty:
    """dfプロパティのテスト"""

    def test_df_property_lazy_load(self, test_loader):
        """dfプロパティが遅延読み込みすること"""
        # 初期状態ではNone
        assert test_loader._df is None

        # プロパティアクセスで読み込み
        df = test_loader.df

        assert df is not None
        assert not df.empty

    def test_df_property_cached(self, test_loader):
        """dfプロパティがキャッシュされること"""
        df1 = test_loader.df
        df2 = test_loader.df

        # 同じオブジェクトを返す
        assert df1 is df2
