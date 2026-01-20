"""E2E（エンドツーエンド）テスト

アプリケーション全体のフローをテストします。
GUIを実際に起動せず、データフローとビジネスロジックの連携を確認します。
"""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_loader import DataLoader
from data_processor import DataProcessor


class TestApplicationStartupFlow:
    """アプリケーション起動フローのテスト"""

    def test_application_initialization_flow(self, test_loader):
        """アプリケーション初期化フローが正しく動作すること"""
        # 1. データの読み込み
        df = test_loader.df
        assert not df.empty

        # 2. DataProcessorの初期化
        processor = DataProcessor(df)
        assert processor.df is not None

        # 3. 期間リストの取得
        periods = test_loader.get_periods()
        assert len(periods) > 0

        # 4. 部門リストの取得
        departments = test_loader.get_departments()
        assert len(departments) > 0

    def test_initial_dashboard_data_flow(self, test_loader):
        """初期ダッシュボードデータフローが正しく動作すること"""
        processor = DataProcessor(test_loader.df)

        # 全社KPIの計算（初期表示時）
        kpi = processor.calculate_kpi()

        # KPIが正常に計算される
        assert kpi['revenue'] > 0
        assert kpi['gross_profit'] > 0

        # 部門別集計
        dept_breakdown = processor.get_department_breakdown()
        assert len(dept_breakdown) > 0


class TestUserInteractionFlow:
    """ユーザー操作フローのテスト"""

    def test_period_selection_flow(self, test_loader):
        """期間選択フローが正しく動作すること"""
        processor = DataProcessor(test_loader.df)

        periods = test_loader.get_periods()

        # 各期間を選択してデータが取得できる
        for period in periods:
            kpi = processor.calculate_kpi(year_month=period)
            assert 'revenue' in kpi
            assert 'operating_income' in kpi

        # 「全期間」選択
        kpi_all = processor.calculate_kpi(year_month=None)
        assert 'revenue' in kpi_all

    def test_department_selection_flow(self, test_loader):
        """部門選択フローが正しく動作すること"""
        processor = DataProcessor(test_loader.df)

        departments = test_loader.get_departments()

        # 各部門を選択してデータが取得できる
        for dept_code, dept_name in departments:
            kpi = processor.calculate_kpi(dept_code=dept_code)
            assert 'revenue' in kpi

            cost = processor.get_cost_structure(dept_code=dept_code)
            assert 'material_cost' in cost

    def test_tab_navigation_data_flow(self, test_loader):
        """タブ切り替え時のデータフローが正しく動作すること"""
        processor = DataProcessor(test_loader.df)

        # ダッシュボードタブ
        dashboard_kpi = processor.calculate_kpi()
        dashboard_dept = processor.get_department_breakdown()
        assert dashboard_kpi is not None
        assert dashboard_dept is not None

        # 部門別分析タブ
        dept_kpi = processor.calculate_kpi(dept_code=210)
        assert dept_kpi is not None

        # 原価分析タブ
        cost_structure = processor.get_cost_structure()
        cost_by_dept = processor.get_cost_breakdown_by_dept()
        assert cost_structure is not None
        assert cost_by_dept is not None

        # 詳細データタブ
        detail_data = processor.get_detail_data(output_type=0)
        assert detail_data is not None


class TestDataRefreshFlow:
    """データ更新フローのテスト"""

    def test_refresh_button_flow(self, test_loader):
        """更新ボタン押下時のフローが正しく動作すること"""
        initial_df = test_loader.df.copy()
        initial_kpi = DataProcessor(initial_df).calculate_kpi()

        # 更新ボタン押下をシミュレート
        test_loader.reload()
        processor = DataProcessor(test_loader.df)

        # データが再読み込みされる
        refreshed_kpi = processor.calculate_kpi()

        # 同じデータなので結果は同じ
        assert refreshed_kpi['revenue'] == initial_kpi['revenue']


class TestDataExportFlow:
    """データエクスポートフローのテスト"""

    def test_csv_export_flow(self, test_loader, tmp_path):
        """CSVエクスポートフローが正しく動作すること"""
        processor = DataProcessor(test_loader.df)

        # 詳細データを取得
        detail = processor.get_detail_data(
            dept_code=210,
            year_month='2025/07',
            output_type=0
        )

        # CSVにエクスポート
        export_path = tmp_path / "export.csv"
        detail.to_csv(export_path, index=False, encoding='utf-8-sig')

        # エクスポートされたファイルを検証
        assert export_path.exists()

        # エクスポートされたデータを読み込んで検証
        exported_df = pd.read_csv(export_path, encoding='utf-8-sig')
        assert len(exported_df) == len(detail)


class TestCompleteUserJourney:
    """完全なユーザージャーニーのテスト"""

    def test_typical_user_session(self, test_loader, tmp_path):
        """典型的なユーザーセッションのシナリオ"""
        # 1. アプリケーション起動
        processor = DataProcessor(test_loader.df)

        # 2. ダッシュボードで全社KPIを確認
        kpi_all = processor.calculate_kpi()
        assert kpi_all['revenue'] > 0
        print(f"全社売上高: {kpi_all['revenue']:,.0f}円")

        # 3. 期間を7月に変更
        kpi_july = processor.calculate_kpi(year_month='2025/07')
        print(f"7月売上高: {kpi_july['revenue']:,.0f}円")

        # 4. 部門別分析タブに切り替え
        departments = test_loader.get_departments()
        selected_dept = departments[0]  # 最初の部門を選択
        dept_kpi = processor.calculate_kpi(dept_code=selected_dept[0])
        print(f"{selected_dept[1]}の売上高: {dept_kpi['revenue']:,.0f}円")

        # 5. 原価分析タブに切り替え
        cost = processor.get_cost_structure(dept_code=selected_dept[0])
        total_cost = cost['material_cost'] + cost['labor_cost'] + cost['expense']
        print(f"原価合計: {total_cost:,.0f}円")

        # 6. 詳細データタブに切り替えてCSVエクスポート
        detail = processor.get_detail_data(
            dept_code=selected_dept[0],
            year_month='2025/07',
            output_type=0
        )

        export_path = tmp_path / "詳細データ_エクスポート.csv"
        detail.to_csv(export_path, index=False, encoding='utf-8-sig')
        assert export_path.exists()

        # 7. データ更新ボタン押下
        test_loader.reload()
        processor = DataProcessor(test_loader.df)
        kpi_refreshed = processor.calculate_kpi()
        assert kpi_refreshed['revenue'] == kpi_all['revenue']


class TestBusinessLogicValidation:
    """ビジネスロジックの検証テスト"""

    def test_profit_calculation_consistency(self, test_loader):
        """利益計算の整合性"""
        processor = DataProcessor(test_loader.df)

        kpi = processor.calculate_kpi(dept_code=210, year_month='2025/07')

        # 売上総利益 = 売上高 - 売上原価
        # Note: 実際のデータ構造によっては直接計算と一致しない場合がある
        # ここでは科目コードから取得した値を検証

        # 営業利益は売上総利益以下
        assert kpi['operating_income'] <= kpi['gross_profit']

        # 経常利益は概ね営業利益に近い（営業外損益で変動）
        # この検証は絶対ではないが、大きな乖離はエラーの兆候

    def test_rate_calculation_bounds(self, test_loader):
        """利益率の範囲検証"""
        processor = DataProcessor(test_loader.df)

        kpi = processor.calculate_kpi(dept_code=210, year_month='2025/07')

        # 売上高が正の場合、利益率は-100%〜100%の範囲内
        if kpi['revenue'] > 0:
            assert -100 <= kpi['gross_margin'] <= 100
            assert -100 <= kpi['op_margin'] <= 100
            assert -100 <= kpi['ord_margin'] <= 100

    def test_cost_structure_completeness(self, test_loader):
        """原価構成の完全性"""
        processor = DataProcessor(test_loader.df)

        cost = processor.get_cost_structure(dept_code=210, year_month='2025/07')

        # 原価要素がすべて0以上
        assert cost['material_cost'] >= 0
        assert cost['labor_cost'] >= 0
        assert cost['expense'] >= 0
        assert cost['mfg_cost'] >= 0


class TestErrorHandling:
    """エラーハンドリングのテスト"""

    def test_graceful_handling_empty_data(self, empty_test_loader):
        """空データでもエラーなく動作すること"""
        # エラーなく初期化
        processor = DataProcessor(empty_test_loader.df)

        # エラーなくKPI計算
        kpi = processor.calculate_kpi()
        assert kpi['revenue'] == 0

        # エラーなく部門別集計
        dept = processor.get_department_breakdown()
        assert dept.empty

    def test_graceful_handling_invalid_department(self, test_loader):
        """無効な部門コードでもエラーなく動作すること"""
        processor = DataProcessor(test_loader.df)

        # 存在しない部門コード
        kpi = processor.calculate_kpi(dept_code=99999)
        assert kpi['revenue'] == 0

    def test_graceful_handling_invalid_period(self, test_loader):
        """無効な期間でもエラーなく動作すること"""
        processor = DataProcessor(test_loader.df)

        # 存在しない期間
        kpi = processor.calculate_kpi(year_month='9999/99')
        assert kpi['revenue'] == 0


class TestPerformance:
    """パフォーマンステスト"""

    def test_kpi_calculation_performance(self, test_loader):
        """KPI計算のパフォーマンス"""
        import time

        processor = DataProcessor(test_loader.df)

        # 100回KPI計算を実行
        start_time = time.time()
        for _ in range(100):
            processor.calculate_kpi()
        elapsed = time.time() - start_time

        # 100回で5秒以内（1回あたり50ms以内）
        assert elapsed < 5.0, f"KPI calculation too slow: {elapsed:.2f}s for 100 iterations"

    def test_department_breakdown_performance(self, test_loader):
        """部門別集計のパフォーマンス"""
        import time

        processor = DataProcessor(test_loader.df)

        # 100回部門別集計を実行
        start_time = time.time()
        for _ in range(100):
            processor.get_department_breakdown()
        elapsed = time.time() - start_time

        # 100回で5秒以内
        assert elapsed < 5.0, f"Department breakdown too slow: {elapsed:.2f}s for 100 iterations"
