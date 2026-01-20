"""データ加工・集計モジュール"""
from typing import Optional
import pandas as pd


class DataProcessor:
    """損益計算書データの加工と集計"""

    # 主要科目コード
    ACCOUNT_CODES = {
        'revenue': 4199,           # 【収入計】
        'cost_of_sales': 5399,     # 【売上原価】
        'gross_profit': 5400,      # 【売上総利益】
        'sga': 6299,               # (販売費及び一般管理費)
        'operating_income': 7000,  # 【営業利益】
        'non_op_revenue': 7199,    # 【営業外収益】
        'non_op_expense': 7599,    # 【営業外費用】
        'ordinary_income': 8000,   # 【経常利益】
        'extra_income': 8199,      # 【特別利益】
        'extra_loss': 8299,        # 【特別損失】
        'pretax_income': 8300,     # 【税引前当期利益】
        'net_income': 9000,        # 【当期利益】
        # 製造原価内訳（出力帳票=1）
        'material_cost': 5419,     # (製)材料費計
        'labor_cost': 5439,        # (製)労務費計
        'expense_cost': 5469,      # (製)経費計
        # 製造原価（出力帳票=0）
        'mfg_cost': 5299,          # 【当期製品製造原価】
    }

    def __init__(self, df: pd.DataFrame):
        """初期化

        Args:
            df: DataLoaderで読み込んだDataFrame
        """
        self.df = df

    def filter_by_department(self, dept_code: Optional[int] = None) -> pd.DataFrame:
        """部門でフィルタリング

        Args:
            dept_code: 部課コード。Noneの場合は全部門

        Returns:
            フィルタリング後のDataFrame
        """
        if dept_code is None:
            return self.df
        return self.df[self.df['部課ｺｰﾄﾞ'] == dept_code]

    def filter_by_period(self, year_month: Optional[str] = None) -> pd.DataFrame:
        """期間でフィルタリング

        Args:
            year_month: 年月 (例: "2025/07")。Noneの場合は全期間

        Returns:
            フィルタリング後のDataFrame
        """
        if year_month is None:
            return self.df
        return self.df[self.df['year_month'] == year_month]

    def get_main_accounts(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """損益計算書の本体（出力帳票=0）を取得"""
        target = df if df is not None else self.df
        return target[target['出力帳票'] == 0]

    def get_cost_breakdown(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """製造原価内訳（出力帳票=1）を取得"""
        target = df if df is not None else self.df
        return target[target['出力帳票'] == 1]

    def get_account_value(
        self,
        df: pd.DataFrame,
        account_code: int,
        value_column: str = '残高'
    ) -> float:
        """特定の科目コードの値を取得

        Args:
            df: 対象のDataFrame
            account_code: 科目コード
            value_column: 取得する値のカラム名 ('残高', '借方', '貸方', '前残高')

        Returns:
            科目の値。見つからない場合は0
        """
        row = df[df['科目ｺｰﾄﾞ'] == account_code]
        if row.empty:
            return 0.0
        return float(row[value_column].iloc[0])

    def calculate_kpi(
        self,
        dept_code: Optional[int] = None,
        year_month: Optional[str] = None
    ) -> dict:
        """KPI（重要経営指標）を計算

        Args:
            dept_code: 部課コード（Noneで全社）
            year_month: 年月（Noneで全期間合計）

        Returns:
            KPIの辞書
        """
        filtered = self.df.copy()

        if dept_code is not None:
            filtered = filtered[filtered['部課ｺｰﾄﾞ'] == dept_code]

        if year_month is not None:
            filtered = filtered[filtered['year_month'] == year_month]

        main_df = self.get_main_accounts(filtered)

        # 部門ごとに集計してから合計
        if dept_code is None:
            # 全社の場合、部門別に科目値を取得して合計
            revenue = 0.0
            cost_of_sales = 0.0
            gross_profit = 0.0
            sga = 0.0
            operating_income = 0.0
            ordinary_income = 0.0
            net_income = 0.0

            for code in main_df['部課ｺｰﾄﾞ'].unique():
                dept_df = main_df[main_df['部課ｺｰﾄﾞ'] == code]
                revenue += self.get_account_value(dept_df, self.ACCOUNT_CODES['revenue'])
                cost_of_sales += self.get_account_value(dept_df, self.ACCOUNT_CODES['cost_of_sales'])
                gross_profit += self.get_account_value(dept_df, self.ACCOUNT_CODES['gross_profit'])
                sga += self.get_account_value(dept_df, self.ACCOUNT_CODES['sga'])
                operating_income += self.get_account_value(dept_df, self.ACCOUNT_CODES['operating_income'])
                ordinary_income += self.get_account_value(dept_df, self.ACCOUNT_CODES['ordinary_income'])
                net_income += self.get_account_value(dept_df, self.ACCOUNT_CODES['net_income'])
        else:
            revenue = self.get_account_value(main_df, self.ACCOUNT_CODES['revenue'])
            cost_of_sales = self.get_account_value(main_df, self.ACCOUNT_CODES['cost_of_sales'])
            gross_profit = self.get_account_value(main_df, self.ACCOUNT_CODES['gross_profit'])
            sga = self.get_account_value(main_df, self.ACCOUNT_CODES['sga'])
            operating_income = self.get_account_value(main_df, self.ACCOUNT_CODES['operating_income'])
            ordinary_income = self.get_account_value(main_df, self.ACCOUNT_CODES['ordinary_income'])
            net_income = self.get_account_value(main_df, self.ACCOUNT_CODES['net_income'])

        # 利益率の計算
        gross_margin = (gross_profit / revenue * 100) if revenue != 0 else 0
        op_margin = (operating_income / revenue * 100) if revenue != 0 else 0
        ord_margin = (ordinary_income / revenue * 100) if revenue != 0 else 0
        net_margin = (net_income / revenue * 100) if revenue != 0 else 0

        return {
            'revenue': revenue,
            'cost_of_sales': cost_of_sales,
            'gross_profit': gross_profit,
            'sga': sga,
            'operating_income': operating_income,
            'ordinary_income': ordinary_income,
            'net_income': net_income,
            'gross_margin': gross_margin,
            'op_margin': op_margin,
            'ord_margin': ord_margin,
            'net_margin': net_margin,
        }

    def get_department_breakdown(self, year_month: Optional[str] = None) -> pd.DataFrame:
        """部門別の売上・利益集計を取得

        Args:
            year_month: 年月（Noneで全期間）

        Returns:
            部門別集計のDataFrame
        """
        filtered = self.df.copy()

        if year_month is not None:
            filtered = filtered[filtered['year_month'] == year_month]

        main_df = self.get_main_accounts(filtered)

        results = []
        for code in sorted(main_df['部課ｺｰﾄﾞ'].unique()):
            dept_df = main_df[main_df['部課ｺｰﾄﾞ'] == code]
            dept_name = dept_df['部課名'].iloc[0] if not dept_df.empty else ''

            revenue = self.get_account_value(dept_df, self.ACCOUNT_CODES['revenue'])
            gross_profit = self.get_account_value(dept_df, self.ACCOUNT_CODES['gross_profit'])
            operating_income = self.get_account_value(dept_df, self.ACCOUNT_CODES['operating_income'])
            ordinary_income = self.get_account_value(dept_df, self.ACCOUNT_CODES['ordinary_income'])

            results.append({
                '部課ｺｰﾄﾞ': code,
                '部課名': dept_name,
                '売上高': revenue,
                '売上総利益': gross_profit,
                '営業利益': operating_income,
                '経常利益': ordinary_income,
                '売上総利益率': (gross_profit / revenue * 100) if revenue != 0 else 0,
                '営業利益率': (operating_income / revenue * 100) if revenue != 0 else 0,
            })

        return pd.DataFrame(results)

    def get_cost_structure(
        self,
        dept_code: Optional[int] = None,
        year_month: Optional[str] = None
    ) -> dict:
        """原価構成を取得

        Args:
            dept_code: 部課コード（Noneで全社）
            year_month: 年月（Noneで全期間）

        Returns:
            原価構成の辞書
        """
        filtered = self.df.copy()

        if dept_code is not None:
            filtered = filtered[filtered['部課ｺｰﾄﾞ'] == dept_code]

        if year_month is not None:
            filtered = filtered[filtered['year_month'] == year_month]

        # 製造原価内訳（出力帳票=1）から材料費・労務費・経費を取得
        cost_df = self.get_cost_breakdown(filtered)
        # 損益計算書本体（出力帳票=0）から製造原価合計を取得
        main_df = self.get_main_accounts(filtered)

        if dept_code is None:
            material_cost = 0.0
            labor_cost = 0.0
            expense_cost = 0.0
            mfg_cost = 0.0

            for code in cost_df['部課ｺｰﾄﾞ'].unique():
                dept_cost = cost_df[cost_df['部課ｺｰﾄﾞ'] == code]
                material_cost += self.get_account_value(dept_cost, self.ACCOUNT_CODES['material_cost'])
                labor_cost += self.get_account_value(dept_cost, self.ACCOUNT_CODES['labor_cost'])
                expense_cost += self.get_account_value(dept_cost, self.ACCOUNT_CODES['expense_cost'])

            for code in main_df['部課ｺｰﾄﾞ'].unique():
                dept_main = main_df[main_df['部課ｺｰﾄﾞ'] == code]
                mfg_cost += self.get_account_value(dept_main, self.ACCOUNT_CODES['mfg_cost'])
        else:
            material_cost = self.get_account_value(cost_df, self.ACCOUNT_CODES['material_cost'])
            labor_cost = self.get_account_value(cost_df, self.ACCOUNT_CODES['labor_cost'])
            expense_cost = self.get_account_value(cost_df, self.ACCOUNT_CODES['expense_cost'])
            mfg_cost = self.get_account_value(main_df, self.ACCOUNT_CODES['mfg_cost'])

        return {
            'material_cost': material_cost,
            'labor_cost': labor_cost,
            'expense': expense_cost,
            'mfg_cost': mfg_cost,
        }

    def get_detail_data(
        self,
        dept_code: Optional[int] = None,
        year_month: Optional[str] = None,
        output_type: int = 0
    ) -> pd.DataFrame:
        """詳細データを取得（テーブル表示用）

        Args:
            dept_code: 部課コード
            year_month: 年月
            output_type: 出力帳票 (0: 損益計算書本体, 1: 製造原価内訳)

        Returns:
            表示用のDataFrame
        """
        filtered = self.df.copy()

        if dept_code is not None:
            filtered = filtered[filtered['部課ｺｰﾄﾞ'] == dept_code]

        if year_month is not None:
            filtered = filtered[filtered['year_month'] == year_month]

        filtered = filtered[filtered['出力帳票'] == output_type]

        display_cols = [
            '部課名', '科目名', '前残高', '借方', '貸方', '残高'
        ]

        result = filtered[display_cols].copy()
        result = result.sort_values(['部課名', '科目名'])

        return result

    def get_sga_breakdown(
        self,
        dept_code: Optional[int] = None,
        year_month: Optional[str] = None
    ) -> pd.DataFrame:
        """販管費の内訳を取得

        Args:
            dept_code: 部課コード（Noneで全社）
            year_month: 年月（Noneで全期間）

        Returns:
            販管費内訳のDataFrame（科目名、金額）
        """
        filtered = self.df.copy()

        if dept_code is not None:
            filtered = filtered[filtered['部課ｺｰﾄﾞ'] == dept_code]

        if year_month is not None:
            filtered = filtered[filtered['year_month'] == year_month]

        # 出力帳票=0（損益計算書本体）から販管費項目を取得
        main_df = self.get_main_accounts(filtered)

        # 販管費の科目コード範囲（6000-6299）
        sga_df = main_df[(main_df['科目ｺｰﾄﾞ'] >= 6000) & (main_df['科目ｺｰﾄﾞ'] < 6299)]

        results = []
        for code in sga_df['科目ｺｰﾄﾞ'].unique():
            item_df = sga_df[sga_df['科目ｺｰﾄﾞ'] == code]
            name = item_df['科目名'].iloc[0] if not item_df.empty else ''
            # 部門別に合計
            total = item_df['残高'].sum()
            if total != 0:  # ゼロの項目は除外
                results.append({
                    '科目ｺｰﾄﾞ': code,
                    '科目名': name,
                    '金額': total
                })

        result_df = pd.DataFrame(results)
        if not result_df.empty:
            result_df = result_df.sort_values('金額', ascending=False)
        return result_df

    def get_cost_breakdown_by_dept(
        self,
        year_month: Optional[str] = None
    ) -> pd.DataFrame:
        """部門別の原価構成を取得

        Args:
            year_month: 年月（Noneで全期間）

        Returns:
            部門別原価構成のDataFrame
        """
        filtered = self.df.copy()

        if year_month is not None:
            filtered = filtered[filtered['year_month'] == year_month]

        cost_df = self.get_cost_breakdown(filtered)
        main_df = self.get_main_accounts(filtered)

        results = []
        for code in sorted(cost_df['部課ｺｰﾄﾞ'].unique()):
            dept_cost = cost_df[cost_df['部課ｺｰﾄﾞ'] == code]
            dept_main = main_df[main_df['部課ｺｰﾄﾞ'] == code]
            dept_name = dept_cost['部課名'].iloc[0] if not dept_cost.empty else ''

            material = self.get_account_value(dept_cost, self.ACCOUNT_CODES['material_cost'])
            labor = self.get_account_value(dept_cost, self.ACCOUNT_CODES['labor_cost'])
            expense = self.get_account_value(dept_cost, self.ACCOUNT_CODES['expense_cost'])
            mfg = self.get_account_value(dept_main, self.ACCOUNT_CODES['mfg_cost'])

            results.append({
                '部課ｺｰﾄﾞ': code,
                '部課名': dept_name,
                '材料費': material,
                '労務費': labor,
                '経費': expense,
                '製造原価': mfg
            })

        return pd.DataFrame(results)
