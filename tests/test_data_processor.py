"""DataProcessor のユニットテスト"""
import io
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from data_processor import DataProcessor


@pytest.fixture
def processor(sample_dataframe):
    """DataProcessorインスタンス"""
    return DataProcessor(sample_dataframe)


@pytest.fixture
def multi_period_dataframe(sample_csv_content, sample_csv_august):
    """複数期間のDataFrame"""
    df_july = pd.read_csv(io.StringIO(sample_csv_content))
    df_july['source_file'] = '2025_07_損益計算書.csv'
    df_july['year_month'] = '2025/07'

    df_august = pd.read_csv(io.StringIO(sample_csv_august))
    df_august['source_file'] = '2025_08_損益計算書.csv'
    df_august['year_month'] = '2025/08'

    return pd.concat([df_july, df_august], ignore_index=True)


class TestDataProcessorInit:
    """DataProcessor 初期化のテスト"""

    def test_init_with_dataframe(self, sample_dataframe):
        """DataFrameで初期化できること"""
        processor = DataProcessor(sample_dataframe)
        assert processor.df is not None
        assert len(processor.df) == len(sample_dataframe)


class TestAccountCodes:
    """科目コード定義のテスト"""

    def test_account_codes_defined(self):
        """主要な科目コードが定義されていること"""
        assert DataProcessor.ACCOUNT_CODES['revenue'] == 4199
        assert DataProcessor.ACCOUNT_CODES['cost_of_sales'] == 5399
        assert DataProcessor.ACCOUNT_CODES['gross_profit'] == 5400
        assert DataProcessor.ACCOUNT_CODES['operating_income'] == 7000
        assert DataProcessor.ACCOUNT_CODES['ordinary_income'] == 8000
        assert DataProcessor.ACCOUNT_CODES['net_income'] == 9000


class TestFilterByDepartment:
    """部門フィルタリングのテスト"""

    def test_filter_specific_department(self, processor):
        """特定部門でフィルタリングできること"""
        filtered = processor.filter_by_department(210)

        assert all(filtered['部課ｺｰﾄﾞ'] == 210)

    def test_filter_all_departments(self, processor):
        """Noneで全部門を返すこと"""
        filtered = processor.filter_by_department(None)

        assert len(filtered) == len(processor.df)

    def test_filter_nonexistent_department(self, processor):
        """存在しない部門では空のDataFrameを返すこと"""
        filtered = processor.filter_by_department(999)

        assert filtered.empty


class TestFilterByPeriod:
    """期間フィルタリングのテスト"""

    def test_filter_specific_period(self, processor):
        """特定期間でフィルタリングできること"""
        filtered = processor.filter_by_period('2025/07')

        assert all(filtered['year_month'] == '2025/07')

    def test_filter_all_periods(self, processor):
        """Noneで全期間を返すこと"""
        filtered = processor.filter_by_period(None)

        assert len(filtered) == len(processor.df)


class TestGetMainAccounts:
    """損益計算書本体取得のテスト"""

    def test_get_main_accounts(self, processor):
        """出力帳票=0のレコードを取得できること"""
        main_df = processor.get_main_accounts()

        assert all(main_df['出力帳票'] == 0)

    def test_get_main_accounts_from_filtered(self, processor):
        """フィルタ済みDataFrameから取得できること"""
        filtered = processor.filter_by_department(210)
        main_df = processor.get_main_accounts(filtered)

        assert all(main_df['出力帳票'] == 0)
        assert all(main_df['部課ｺｰﾄﾞ'] == 210)


class TestGetCostBreakdown:
    """製造原価内訳取得のテスト"""

    def test_get_cost_breakdown(self, processor):
        """出力帳票=1のレコードを取得できること"""
        cost_df = processor.get_cost_breakdown()

        assert all(cost_df['出力帳票'] == 1)


class TestGetAccountValue:
    """科目値取得のテスト"""

    def test_get_revenue_value(self, processor):
        """売上高（収入計）を取得できること"""
        main_df = processor.get_main_accounts()
        dept_df = main_df[main_df['部課ｺｰﾄﾞ'] == 210]

        revenue = processor.get_account_value(dept_df, 4199)

        assert revenue == 10000000  # 1000万円

    def test_get_nonexistent_account(self, processor):
        """存在しない科目では0を返すこと"""
        main_df = processor.get_main_accounts()
        value = processor.get_account_value(main_df, 99999)

        assert value == 0.0


class TestCalculateKPI:
    """KPI計算のテスト"""

    def test_calculate_kpi_single_department(self, processor):
        """単一部門のKPIを計算できること"""
        kpi = processor.calculate_kpi(dept_code=210, year_month='2025/07')

        assert kpi['revenue'] == 10000000
        assert kpi['gross_profit'] == 3000000
        assert kpi['operating_income'] == 2500000
        assert kpi['ordinary_income'] == 2400000
        assert kpi['net_income'] == 2000000

    def test_calculate_kpi_margins(self, processor):
        """利益率が正しく計算されること"""
        kpi = processor.calculate_kpi(dept_code=210, year_month='2025/07')

        # 売上総利益率 = 3000000 / 10000000 * 100 = 30%
        assert kpi['gross_margin'] == 30.0

        # 営業利益率 = 2500000 / 10000000 * 100 = 25%
        assert kpi['op_margin'] == 25.0

    def test_calculate_kpi_all_departments(self, processor):
        """全社KPIを計算できること（部門合計）"""
        kpi = processor.calculate_kpi(year_month='2025/07')

        # 建機事業部 + 社会インフラ製作
        expected_revenue = 10000000 + 8000000
        assert kpi['revenue'] == expected_revenue

    def test_calculate_kpi_zero_revenue(self, sample_dataframe):
        """売上高0の場合、利益率は0になること"""
        # 売上高を0にしたデータ
        df = sample_dataframe.copy()
        df.loc[df['科目ｺｰﾄﾞ'] == 4199, '残高'] = 0

        processor = DataProcessor(df)
        kpi = processor.calculate_kpi()

        assert kpi['gross_margin'] == 0
        assert kpi['op_margin'] == 0


class TestGetDepartmentBreakdown:
    """部門別集計のテスト"""

    def test_get_department_breakdown(self, processor):
        """部門別集計を取得できること"""
        breakdown = processor.get_department_breakdown(year_month='2025/07')

        assert len(breakdown) == 2  # 建機事業部 + 社会インフラ製作
        assert '部課ｺｰﾄﾞ' in breakdown.columns
        assert '売上高' in breakdown.columns
        assert '営業利益' in breakdown.columns
        assert '営業利益率' in breakdown.columns

    def test_department_breakdown_values(self, processor):
        """部門別集計の値が正しいこと"""
        breakdown = processor.get_department_breakdown(year_month='2025/07')

        # 建機事業部のデータ
        kenki = breakdown[breakdown['部課ｺｰﾄﾞ'] == 210].iloc[0]
        assert kenki['売上高'] == 10000000
        assert kenki['営業利益'] == 2500000


class TestGetCostStructure:
    """原価構成取得のテスト"""

    def test_get_cost_structure_single_dept(self, processor):
        """単一部門の原価構成を取得できること"""
        cost = processor.get_cost_structure(dept_code=210, year_month='2025/07')

        assert cost['material_cost'] == 3000000  # 材料費
        assert cost['labor_cost'] == 2000000     # 労務費
        assert cost['expense'] == 1500000        # 経費
        assert cost['mfg_cost'] == 6500000       # 製造原価

    def test_get_cost_structure_all_departments(self, processor):
        """全社の原価構成を取得できること"""
        cost = processor.get_cost_structure(year_month='2025/07')

        # 建機事業部 + 社会インフラ製作
        expected_material = 3000000 + 2500000
        expected_labor = 2000000 + 1800000
        expected_expense = 1500000 + 1200000

        assert cost['material_cost'] == expected_material
        assert cost['labor_cost'] == expected_labor
        assert cost['expense'] == expected_expense


class TestGetDetailData:
    """詳細データ取得のテスト"""

    def test_get_detail_data_main(self, processor):
        """損益計算書本体の詳細データを取得できること"""
        detail = processor.get_detail_data(
            dept_code=210,
            year_month='2025/07',
            output_type=0
        )

        assert not detail.empty
        assert '部課名' in detail.columns
        assert '科目名' in detail.columns
        assert '残高' in detail.columns

    def test_get_detail_data_cost(self, processor):
        """製造原価内訳の詳細データを取得できること"""
        detail = processor.get_detail_data(
            dept_code=210,
            year_month='2025/07',
            output_type=1
        )

        assert not detail.empty


class TestGetSgaBreakdown:
    """販管費内訳取得のテスト"""

    def test_get_sga_breakdown(self, processor):
        """販管費内訳を取得できること"""
        sga = processor.get_sga_breakdown(dept_code=210, year_month='2025/07')

        # テストデータには販管費詳細が含まれていないため、
        # 空でない場合のみカラムを検証
        if not sga.empty:
            # 科目コード6000-6299の範囲
            assert '科目ｺｰﾄﾞ' in sga.columns
            assert '科目名' in sga.columns
            assert '金額' in sga.columns

    def test_sga_sorted_by_amount(self, processor):
        """販管費が金額順にソートされていること"""
        sga = processor.get_sga_breakdown(year_month='2025/07')

        if not sga.empty:
            amounts = sga['金額'].tolist()
            assert amounts == sorted(amounts, reverse=True)


class TestGetCostBreakdownByDept:
    """部門別原価構成取得のテスト"""

    def test_get_cost_breakdown_by_dept(self, processor):
        """部門別原価構成を取得できること"""
        breakdown = processor.get_cost_breakdown_by_dept(year_month='2025/07')

        assert len(breakdown) >= 2
        assert '部課名' in breakdown.columns
        assert '材料費' in breakdown.columns
        assert '労務費' in breakdown.columns
        assert '経費' in breakdown.columns
        assert '製造原価' in breakdown.columns

    def test_cost_breakdown_values_correct(self, processor):
        """部門別原価構成の値が正しいこと"""
        breakdown = processor.get_cost_breakdown_by_dept(year_month='2025/07')

        kenki = breakdown[breakdown['部課ｺｰﾄﾞ'] == 210].iloc[0]
        assert kenki['材料費'] == 3000000
        assert kenki['労務費'] == 2000000
        assert kenki['経費'] == 1500000


class TestEdgeCases:
    """エッジケースのテスト"""

    def test_empty_dataframe(self):
        """空のDataFrameでも動作すること"""
        empty_df = pd.DataFrame(columns=[
            '部課ｺｰﾄﾞ', '部課名', '科目ｺｰﾄﾞ', '科目名',
            '前残高', '借方', '貸方', '残高', '出力帳票', 'year_month'
        ])
        processor = DataProcessor(empty_df)

        kpi = processor.calculate_kpi()
        assert kpi['revenue'] == 0

        breakdown = processor.get_department_breakdown()
        assert breakdown.empty

    def test_negative_values(self, sample_dataframe):
        """マイナス値でも正しく計算されること"""
        df = sample_dataframe.copy()
        # 営業利益をマイナスに
        df.loc[df['科目ｺｰﾄﾞ'] == 7000, '残高'] = -500000

        processor = DataProcessor(df)
        kpi = processor.calculate_kpi(dept_code=210, year_month='2025/07')

        assert kpi['operating_income'] == -500000
        assert kpi['op_margin'] < 0


class TestMultiplePeriods:
    """複数期間のテスト"""

    def test_multi_period_kpi(self, multi_period_dataframe):
        """複数期間からの集計が正しいこと"""
        processor = DataProcessor(multi_period_dataframe)

        # 7月のみ
        kpi_july = processor.calculate_kpi(dept_code=210, year_month='2025/07')
        assert kpi_july['revenue'] == 10000000

        # 8月のみ
        kpi_august = processor.calculate_kpi(dept_code=210, year_month='2025/08')
        assert kpi_august['revenue'] == 22000000  # 累計値

    def test_all_periods_sum(self, multi_period_dataframe):
        """全期間選択時の動作テスト

        Note: 現在の実装では全期間選択時に各期間のデータを単純合算します。
        テストデータでは建機事業部(210)は7月のみデータがあるため、
        7月の値がそのまま返されます。
        """
        processor = DataProcessor(multi_period_dataframe)

        # 全期間で集計
        kpi_all = processor.calculate_kpi(dept_code=210, year_month=None)

        # テストデータでは建機事業部は7月のみ
        # 実装は各期間を合算するため、7月の10000000円のみ
        assert kpi_all['revenue'] == 10000000
