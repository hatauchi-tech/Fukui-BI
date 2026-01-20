"""ビュー統合テスト

注意: このテストはGUIコンポーネントを実際に起動せず、
ビューで使用されるデータ処理ロジックの統合をテストします。
"""
import io
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_loader import DataLoader
from data_processor import DataProcessor


class TestDashboardViewIntegration:
    """ダッシュボードビューの統合テスト"""

    def test_kpi_data_for_dashboard(self, test_loader):
        """ダッシュボード用KPIデータが取得できること"""
        processor = DataProcessor(test_loader.df)

        # ダッシュボードで表示するKPI
        kpi = processor.calculate_kpi(year_month='2025/07')

        # 必須フィールドの存在確認
        required_fields = [
            'revenue', 'gross_profit', 'operating_income', 'ordinary_income',
            'gross_margin', 'op_margin', 'ord_margin'
        ]

        for field in required_fields:
            assert field in kpi, f"Missing KPI field: {field}"

    def test_department_breakdown_for_dashboard(self, test_loader):
        """ダッシュボード用部門別集計データが取得できること"""
        processor = DataProcessor(test_loader.df)

        # 部門別集計
        dept_df = processor.get_department_breakdown(year_month='2025/07')

        # 必須カラムの存在確認
        required_columns = ['部課名', '売上高', '営業利益', '営業利益率']
        for col in required_columns:
            assert col in dept_df.columns, f"Missing column: {col}"

        # 「共通」部門を除外したデータがあること
        chart_df = dept_df[dept_df['部課名'] != '共通']
        assert len(chart_df) >= 2

    def test_pie_chart_data_positive_only(self, test_loader):
        """円グラフ用に正の売上高のみ取得できること"""
        processor = DataProcessor(test_loader.df)

        dept_df = processor.get_department_breakdown(year_month='2025/07')
        chart_df = dept_df[dept_df['部課名'] != '共通']
        positive_revenue_df = chart_df[chart_df['売上高'] > 0]

        # 正の売上高を持つ部門がある
        assert len(positive_revenue_df) >= 2

        # 円グラフ用データ
        labels = positive_revenue_df['部課名'].tolist()
        values = positive_revenue_df['売上高'].tolist()

        assert len(labels) == len(values)
        assert all(v > 0 for v in values)


class TestDepartmentViewIntegration:
    """部門別分析ビューの統合テスト"""

    def test_department_list(self, test_loader):
        """部門リストが取得できること"""
        departments = test_loader.get_departments()

        # 部門がある
        assert len(departments) >= 2

        # コード順にソートされている
        codes = [code for code, name in departments]
        assert codes == sorted(codes)

    def test_department_kpi(self, test_loader):
        """部門別KPIが取得できること"""
        processor = DataProcessor(test_loader.df)

        # 建機事業部のKPI
        kpi = processor.calculate_kpi(dept_code=210, year_month='2025/07')

        assert kpi['revenue'] == 10000000
        assert kpi['gross_margin'] == 30.0  # (3000000/10000000)*100

    def test_monthly_trend_data(self, test_loader):
        """月次推移データが取得できること"""
        processor = DataProcessor(test_loader.df)

        periods = test_loader.get_periods()

        # 複数期間がある場合
        if len(periods) > 1:
            revenues = []
            op_incomes = []

            for period in periods:
                p_kpi = processor.calculate_kpi(
                    dept_code=210,
                    year_month=period
                )
                revenues.append(p_kpi['revenue'] / 1_000_000)
                op_incomes.append(p_kpi['operating_income'] / 1_000_000)

            assert len(revenues) == len(periods)
            assert len(op_incomes) == len(periods)

    def test_profit_composition_data(self, test_loader):
        """利益構成データが取得できること"""
        processor = DataProcessor(test_loader.df)

        kpi = processor.calculate_kpi(dept_code=210, year_month='2025/07')

        profit_data = [
            ('売上総利益', kpi['gross_profit']),
            ('営業利益', kpi['operating_income']),
            ('経常利益', kpi['ordinary_income']),
        ]

        # 利益の階層が正しい（売上総利益 > 営業利益 >= 経常利益）
        assert profit_data[0][1] >= profit_data[1][1]


class TestCostAnalysisViewIntegration:
    """原価分析ビューの統合テスト"""

    def test_cost_structure_data(self, test_loader):
        """原価構成データが取得できること"""
        processor = DataProcessor(test_loader.df)

        cost = processor.get_cost_structure(year_month='2025/07')

        # 原価要素が含まれる
        assert 'material_cost' in cost
        assert 'labor_cost' in cost
        assert 'expense' in cost
        assert 'mfg_cost' in cost

        # 正の値がある（テストデータでは）
        assert cost['material_cost'] > 0
        assert cost['labor_cost'] > 0
        assert cost['expense'] > 0

    def test_cost_pie_chart_data(self, test_loader):
        """原価円グラフ用データが取得できること"""
        processor = DataProcessor(test_loader.df)

        cost = processor.get_cost_structure(year_month='2025/07')

        cost_labels = ['材料費', '労務費', '経費']
        cost_values = [
            cost['material_cost'],
            cost['labor_cost'],
            cost['expense']
        ]

        assert len(cost_labels) == len(cost_values)
        assert any(v > 0 for v in cost_values)

    def test_department_cost_comparison(self, test_loader):
        """部門別原価比較データが取得できること"""
        processor = DataProcessor(test_loader.df)

        dept_cost_df = processor.get_cost_breakdown_by_dept(year_month='2025/07')

        # 「共通」を除外
        dept_cost_df = dept_cost_df[dept_cost_df['部課名'] != '共通']

        assert len(dept_cost_df) >= 2

        # 必須カラム
        required_cols = ['部課名', '材料費', '労務費', '経費', '製造原価']
        for col in required_cols:
            assert col in dept_cost_df.columns

    def test_stacked_bar_data(self, test_loader):
        """積み上げ棒グラフ用データが取得できること"""
        processor = DataProcessor(test_loader.df)

        dept_cost_df = processor.get_cost_breakdown_by_dept(year_month='2025/07')
        dept_cost_df = dept_cost_df[dept_cost_df['部課名'] != '共通']

        # 積み上げ用データ構造
        labels = dept_cost_df['部課名'].tolist()
        data_dict = {
            '材料費': dept_cost_df['材料費'].tolist(),
            '労務費': dept_cost_df['労務費'].tolist(),
            '経費': dept_cost_df['経費'].tolist()
        }

        # 各系列のデータ長がラベル数と一致
        for key, values in data_dict.items():
            assert len(values) == len(labels)

    def test_sga_breakdown(self, test_loader):
        """販管費内訳が取得できること"""
        processor = DataProcessor(test_loader.df)

        sga_df = processor.get_sga_breakdown(year_month='2025/07')

        # 販管費データの構造確認
        if not sga_df.empty:
            assert '科目名' in sga_df.columns
            assert '金額' in sga_df.columns

            # 金額順にソートされている
            amounts = sga_df['金額'].tolist()
            assert amounts == sorted(amounts, reverse=True)


class TestDetailViewIntegration:
    """詳細データビューの統合テスト"""

    def test_detail_data_retrieval(self, test_loader):
        """詳細データが取得できること"""
        processor = DataProcessor(test_loader.df)

        # 損益計算書本体
        detail = processor.get_detail_data(
            dept_code=210,
            year_month='2025/07',
            output_type=0
        )

        assert not detail.empty
        assert '部課名' in detail.columns
        assert '科目名' in detail.columns
        assert '残高' in detail.columns

    def test_detail_data_filtering(self, test_loader):
        """詳細データのフィルタリングが正しいこと"""
        processor = DataProcessor(test_loader.df)

        # 全部門、全期間
        detail_all = processor.get_detail_data(output_type=0)

        # 特定部門
        detail_dept = processor.get_detail_data(
            dept_code=210,
            output_type=0
        )

        # 特定部門のデータは全体より少ない
        assert len(detail_dept) < len(detail_all)

    def test_detail_data_for_export(self, test_loader):
        """エクスポート用詳細データが取得できること"""
        processor = DataProcessor(test_loader.df)

        detail = processor.get_detail_data(
            dept_code=210,
            year_month='2025/07',
            output_type=0
        )

        # CSVエクスポート可能なDataFrame
        assert hasattr(detail, 'to_csv')

        # 必要なカラムが存在
        required_cols = ['部課名', '科目名', '前残高', '借方', '貸方', '残高']
        for col in required_cols:
            assert col in detail.columns


class TestPeriodFiltering:
    """期間フィルタリングの統合テスト"""

    def test_period_change_updates_data(self, test_loader):
        """期間変更でデータが更新されること"""
        processor = DataProcessor(test_loader.df)

        # 7月のKPI
        kpi_july = processor.calculate_kpi(year_month='2025/07')

        # 8月のKPI
        kpi_august = processor.calculate_kpi(year_month='2025/08')

        # 異なる値（8月は累計なので大きい）
        assert kpi_july['revenue'] != kpi_august['revenue']

    def test_all_periods_aggregation(self, test_loader):
        """全期間選択で集計されること"""
        processor = DataProcessor(test_loader.df)

        # 全期間（全社、全部門）
        kpi_all = processor.calculate_kpi(year_month=None)

        # 全期間のKPIが取得できることを確認
        assert 'revenue' in kpi_all
        assert kpi_all['revenue'] > 0

        # 個別期間も取得できることを確認
        kpi_july = processor.calculate_kpi(year_month='2025/07')
        kpi_august = processor.calculate_kpi(year_month='2025/08')
        assert kpi_july['revenue'] > 0
        assert kpi_august['revenue'] > 0


class TestDataRefresh:
    """データ更新の統合テスト"""

    def test_data_reload(self, test_loader):
        """データの再読み込みが正しく動作すること"""
        # 初回読み込み
        df1 = test_loader.df.copy()
        files1 = test_loader.loaded_files.copy()

        # 再読み込み
        test_loader.reload()

        # データが再読み込みされている
        assert test_loader.loaded_files == files1
        assert len(test_loader.df) == len(df1)

    def test_processor_update_after_reload(self, test_loader):
        """再読み込み後にProcessorが更新されること"""
        processor = DataProcessor(test_loader.df)
        kpi1 = processor.calculate_kpi()

        # 再読み込み後にProcessor再作成
        test_loader.reload()
        processor = DataProcessor(test_loader.df)
        kpi2 = processor.calculate_kpi()

        # 同じデータなので同じ結果
        assert kpi1['revenue'] == kpi2['revenue']


class TestEdgeCasesIntegration:
    """エッジケースの統合テスト"""

    def test_empty_data_handling(self, empty_test_loader):
        """空データでもクラッシュしないこと"""
        processor = DataProcessor(empty_test_loader.df)

        # KPI計算
        kpi = processor.calculate_kpi()
        assert kpi['revenue'] == 0

        # 部門別集計
        dept_df = processor.get_department_breakdown()
        assert dept_df.empty

        # 原価構成
        cost = processor.get_cost_structure()
        assert cost['mfg_cost'] == 0

    def test_nonexistent_department(self, test_loader):
        """存在しない部門でもクラッシュしないこと"""
        processor = DataProcessor(test_loader.df)

        kpi = processor.calculate_kpi(dept_code=999)

        assert kpi['revenue'] == 0

    def test_nonexistent_period(self, test_loader):
        """存在しない期間でもクラッシュしないこと"""
        processor = DataProcessor(test_loader.df)

        kpi = processor.calculate_kpi(year_month='1999/01')

        assert kpi['revenue'] == 0
