"""CSVデータ読み込みモジュール"""
import os
import re
from pathlib import Path
from typing import Optional
import pandas as pd


class DataLoader:
    """損益計算書CSVの読み込みと管理"""

    # CSV列名の定義
    COLUMN_NAMES = [
        '事業所ｺｰﾄﾞ', '事業所名', '事業所略名', '部課ｺｰﾄﾞ', '部課名', '部課略名',
        '出力帳票', '改頁№', 'SEQNO', '科目ｺｰﾄﾞ', '補助ｺｰﾄﾞ', '科目名',
        '補助科目名', '科目略名', '貸借区分', '属性区分', '罫線区分',
        '前残高', '借方', '貸方', '残高', '開始年月', '終了年月'
    ]

    # 数値カラム
    NUMERIC_COLUMNS = ['前残高', '借方', '貸方', '残高']

    def __init__(self, data_folder: str = "損益計算書"):
        """初期化

        Args:
            data_folder: CSVデータが格納されているフォルダ名
        """
        self.base_path = Path(__file__).parent.parent
        self.data_folder = self.base_path / data_folder
        self._df: Optional[pd.DataFrame] = None
        self._loaded_files: list[str] = []

    @property
    def df(self) -> pd.DataFrame:
        """読み込み済みのDataFrameを取得"""
        if self._df is None:
            self.load_all()
        return self._df

    @property
    def loaded_files(self) -> list[str]:
        """読み込んだファイル一覧"""
        return self._loaded_files

    def _extract_year_month_from_filename(self, filename: str) -> Optional[str]:
        """ファイル名から年月を抽出

        Args:
            filename: CSVファイル名 (例: 2025_07_損益計算書.csv)

        Returns:
            年月文字列 (例: 2025/07) または None
        """
        pattern = r'(\d{4})_(\d{2})_'
        match = re.search(pattern, filename)
        if match:
            year, month = match.groups()
            return f"{year}/{month}"
        return None

    def load_file(self, filepath: Path) -> pd.DataFrame:
        """単一のCSVファイルを読み込む

        Args:
            filepath: CSVファイルのパス

        Returns:
            読み込んだDataFrame
        """
        df = pd.read_csv(
            filepath,
            encoding='utf-8',
            dtype={
                '事業所ｺｰﾄﾞ': int,
                '部課ｺｰﾄﾞ': int,
                '出力帳票': int,
                '改頁№': int,
                'SEQNO': int,
                '科目ｺｰﾄﾞ': int,
                '補助ｺｰﾄﾞ': int,
                '貸借区分': int,
                '属性区分': int,
                '罫線区分': int,
            }
        )

        # 数値カラムの処理（空白やNaNを0に変換）
        for col in self.NUMERIC_COLUMNS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # ファイル名から年月を推定、できなければCSV内の値を使用
        filename = filepath.name
        year_month = self._extract_year_month_from_filename(filename)

        if year_month is None and '開始年月' in df.columns:
            first_valid = df['開始年月'].dropna().iloc[0] if not df['開始年月'].dropna().empty else None
            year_month = first_valid

        df['source_file'] = filename
        df['year_month'] = year_month

        return df

    def load_all(self) -> pd.DataFrame:
        """損益計算書フォルダ内の全CSVを読み込み統合

        Returns:
            統合されたDataFrame
        """
        if not self.data_folder.exists():
            self.data_folder.mkdir(parents=True)
            self._df = pd.DataFrame(columns=self.COLUMN_NAMES + ['source_file', 'year_month'])
            return self._df

        csv_files = sorted(self.data_folder.glob("*.csv"))

        if not csv_files:
            self._df = pd.DataFrame(columns=self.COLUMN_NAMES + ['source_file', 'year_month'])
            return self._df

        dfs = []
        self._loaded_files = []

        for filepath in csv_files:
            try:
                df = self.load_file(filepath)
                dfs.append(df)
                self._loaded_files.append(filepath.name)
            except Exception as e:
                print(f"警告: {filepath.name} の読み込みに失敗しました: {e}")

        if dfs:
            self._df = pd.concat(dfs, ignore_index=True)
        else:
            self._df = pd.DataFrame(columns=self.COLUMN_NAMES + ['source_file', 'year_month'])

        return self._df

    def reload(self) -> pd.DataFrame:
        """データを再読み込み"""
        self._df = None
        self._loaded_files = []
        return self.load_all()

    def get_departments(self) -> list[tuple[int, str]]:
        """部課一覧を取得

        Returns:
            (部課コード, 部課名) のリスト
        """
        df = self.df  # プロパティ経由でアクセス（load_allを呼び出す）
        if df.empty:
            return []

        dept_df = df[['部課ｺｰﾄﾞ', '部課名']].drop_duplicates()
        dept_df = dept_df.sort_values('部課ｺｰﾄﾞ')
        return list(zip(dept_df['部課ｺｰﾄﾞ'], dept_df['部課名']))

    def get_periods(self) -> list[str]:
        """対象期間一覧を取得

        Returns:
            年月のリスト (例: ['2025/07', '2025/08'])
        """
        df = self.df  # プロパティ経由でアクセス（load_allを呼び出す）
        if df.empty:
            return []

        periods = df['year_month'].dropna().unique().tolist()
        return sorted(periods)

    def get_latest_period(self) -> Optional[str]:
        """最新の対象期間を取得"""
        periods = self.get_periods()
        return periods[-1] if periods else None
