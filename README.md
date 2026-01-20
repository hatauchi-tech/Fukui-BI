<div align="center">

# 🏭 福井BI

### 損益計算書 ビジネスインテリジェンス ツール

<br>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![License](https://img.shields.io/badge/License-Internal_Use-2C3E50?style=for-the-badge)](./LICENSE)

<br>

**福井鐵工株式会社向け 経営分析ダッシュボード**

月次損益計算書データを可視化し、迅速な経営判断をサポートします

<br>

---

</div>

<br>

## ✨ 特徴

<table>
<tr>
<td width="50%">

### 📊 リアルタイムKPI表示
売上高・売上総利益・営業利益・経常利益・当期利益を一目で把握

### 🏢 部門別分析
8部門の業績を個別に深掘り分析、複数部門の比較も可能

</td>
<td width="50%">

### 💰 原価分析
製造原価（材料費・労務費・経費）と販管費の内訳を可視化

### 📈 インタラクティブグラフ
円グラフ・棒グラフで構成比と推移を直感的に理解

</td>
</tr>
</table>

<br>

## 🚀 クイックスタート

```bash
# 1. セットアップ（初回のみ）
setup.bat

# 2. アプリケーション起動
損益計算書BI.bat
```

> 💡 CSVファイルは `損益計算書/` フォルダに `YYYY_MM_損益計算書.csv` 形式で配置してください

<br>

## 📂 対象部門

| コード | 部課名 | | コード | 部課名 |
|:------:|:-------|:---:|:------:|:-------|
| `210` | 建機事業部 | | `250` | 民間リピート製作 |
| `220` | 社会インフラ製作 | | `260` | その他製作 |
| `230` | 社会インフラ架設 | | `270` | わかえ共通 |
| `240` | 特機 | | `900` | 共通 |

<br>

## 🖥️ 画面構成

```
┌─────────────────────────────────────────────────────────────┐
│  全社サマリー │ 部門別分析 │ 原価分析 │ 詳細データ │ ガイド  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│   │ 売上高  │ │売上総利益│ │営業利益 │ │経常利益 │          │
│   │  KPI    │ │   KPI   │ │   KPI   │ │   KPI   │          │
│   └─────────┘ └─────────┘ └─────────┘ └─────────┘          │
│                                                             │
│   ┌─────────────────────┐ ┌─────────────────────┐          │
│   │                     │ │                     │          │
│   │    売上構成比       │ │   営業利益比較      │          │
│   │     円グラフ        │ │     棒グラフ        │          │
│   │                     │ │                     │          │
│   └─────────────────────┘ └─────────────────────┘          │
│                                                             │
│   ┌─────────────────────────────────────────────┐          │
│   │           部門別サマリーテーブル            │          │
│   └─────────────────────────────────────────────┘          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

<br>

## 🛠️ 技術スタック

<div align="center">

| カテゴリ | 技術 | バージョン |
|:--------:|:----:|:----------:|
| **言語** | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) | 3.11+ |
| **GUI** | ![Tkinter](https://img.shields.io/badge/tkinter-FF6F00?style=flat-square&logo=python&logoColor=white) + ttkbootstrap | 1.10+ |
| **データ処理** | ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white) | 2.0+ |
| **可視化** | ![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=flat-square&logo=python&logoColor=white) | 3.7+ |

</div>

<br>

## 📁 ディレクトリ構成

<details>
<summary><b>クリックして展開</b></summary>

```
Fukui-BI/
│
├── 📄 損益計算書BI.bat          # 起動用バッチファイル
├── 📄 setup.bat                 # 環境セットアップ
├── 📄 requirements.txt          # 依存パッケージ
│
├── 📂 損益計算書/               # CSVデータ格納
│   └── YYYY_MM_損益計算書.csv
│
├── 📂 src/
│   ├── main.py                  # エントリーポイント
│   ├── app.py                   # メインアプリケーション
│   ├── data_loader.py           # データ読み込み
│   ├── data_processor.py        # データ加工・集計
│   │
│   ├── 📂 components/           # UIコンポーネント
│   │   ├── theme.py             # テーマ設定
│   │   ├── kpi_card.py          # KPIカード
│   │   ├── charts.py            # グラフ
│   │   ├── data_table.py        # テーブル
│   │   └── responsive.py        # レスポンシブ対応
│   │
│   └── 📂 views/                # 画面ビュー
│       ├── dashboard.py         # 全社サマリー
│       ├── department.py        # 部門別分析
│       ├── cost_analysis.py     # 原価分析
│       ├── detail_view.py       # 詳細データ
│       └── guide.py             # ガイド
│
└── 📂 tests/                    # テストファイル
```

</details>

<br>

## 📋 主要科目コード

<details>
<summary><b>クリックして展開</b></summary>

| 科目 | コード | 説明 |
|:-----|:------:|:-----|
| 売上高（収入計） | `4199` | 全部門の売上合計 |
| 売上原価 | `5399` | 製造にかかった原価 |
| 売上総利益 | `5400` | 売上高 − 売上原価 |
| 販管費 | `6299` | 販売費及び一般管理費 |
| 営業利益 | `7000` | 売上総利益 − 販管費 |
| 経常利益 | `8000` | 営業利益 ± 営業外損益 |
| 当期利益 | `9000` | 最終的な純利益 |

</details>

<br>

## 💻 動作環境

- **OS**: Windows 10 / 11
- **Python**: 3.11 以上
- **メモリ**: 4GB 以上推奨

<br>

## 📥 インストール

### 方法1: 自動セットアップ（推奨）

```batch
setup.bat
```

### 方法2: 手動インストール

```bash
pip install -r requirements.txt
```

<br>

---

<div align="center">

**福井鐵工株式会社** | 社内利用限定

<sub>Built with ❤️ for better business decisions</sub>

</div>
