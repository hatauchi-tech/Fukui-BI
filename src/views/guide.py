"""経営指標ガイド画面"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class GuideView(ttk.Frame):
    """経営指標ガイド画面"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self._create_widgets()

    def _create_widgets(self):
        """ウィジェットを作成"""
        # スクロール可能なキャンバス
        canvas = ttk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor=NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        content = self.scrollable_frame

        # ヘッダー
        header = ttk.Frame(content)
        header.pack(fill=X, padx=20, pady=(20, 10))

        ttk.Label(
            header,
            text="経営指標ガイド",
            font=("", 16, "bold")
        ).pack(side=LEFT)

        # セクション1: 主要経営指標の算出方法
        self._create_kpi_section(content)

        # セクション2: 指標の目安
        self._create_benchmark_section(content)

        # セクション3: グラフの見方
        self._create_chart_guide_section(content)

        # セクション4: 分析のポイント
        self._create_analysis_section(content)

        # セクション5: 改善アクション
        self._create_action_section(content)

        # セクション6: 用語集
        self._create_glossary_section(content)

    def _create_section_header(self, parent, title: str):
        """セクションヘッダーを作成"""
        section = ttk.LabelFrame(parent, text=title)
        section.pack(fill=X, padx=20, pady=10)
        return section

    def _create_table(self, parent, headers: list, rows: list, widths: list = None):
        """テーブルを作成"""
        # ヘッダー行
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=X, pady=(0, 5))

        if widths is None:
            widths = [20] * len(headers)

        for i, (header, width) in enumerate(zip(headers, widths)):
            ttk.Label(
                header_frame,
                text=header,
                font=("", 9, "bold"),
                width=width,
                anchor=W
            ).pack(side=LEFT, padx=2)

        ttk.Separator(parent, orient=HORIZONTAL).pack(fill=X, pady=2)

        # データ行
        for row in rows:
            row_frame = ttk.Frame(parent)
            row_frame.pack(fill=X, pady=1)

            for i, (cell, width) in enumerate(zip(row, widths)):
                ttk.Label(
                    row_frame,
                    text=cell,
                    width=width,
                    anchor=W,
                    wraplength=width * 8 if width > 30 else 0
                ).pack(side=LEFT, padx=2)

    def _create_kpi_section(self, parent):
        """主要経営指標の算出方法セクション"""
        section = self._create_section_header(parent, "1. 主要経営指標の算出方法")

        content = ttk.Frame(section)
        content.pack(fill=X, padx=10, pady=10)

        # 収益性指標
        ttk.Label(
            content,
            text="■ 収益性指標",
            font=("", 10, "bold")
        ).pack(anchor=W, pady=(0, 5))

        headers = ['指標名', '計算式', '意味・目的']
        rows = [
            ('売上総利益率（粗利率）', '(売上高-売上原価)÷売上高×100', '製品の基本的な収益力。製造効率や価格設定の妥当性を評価'),
            ('営業利益率', '営業利益÷売上高×100', '本業での収益力。販管費を含めた事業全体の効率性を評価'),
            ('経常利益率', '経常利益÷売上高×100', '財務活動を含めた通常の企業活動の収益力'),
            ('当期純利益率', '当期利益÷売上高×100', '最終的な収益力。税引後の実質的な利益率'),
        ]
        self._create_table(content, headers, rows, widths=[18, 25, 45])

        ttk.Separator(content, orient=HORIZONTAL).pack(fill=X, pady=10)

        # 原価・費用関連指標
        ttk.Label(
            content,
            text="■ 原価・費用関連指標",
            font=("", 10, "bold")
        ).pack(anchor=W, pady=(0, 5))

        rows2 = [
            ('売上原価率', '売上原価÷売上高×100', '売上に対する製造コストの割合。低いほど効率的'),
            ('販管費率', '販管費÷売上高×100', '売上に対する間接費用の割合。管理効率の指標'),
            ('材料費率', '材料費÷売上高×100', '売上に対する材料費の割合。調達効率の指標'),
            ('労務費率', '労務費÷売上高×100', '売上に対する人件費の割合。生産性の指標'),
        ]
        self._create_table(content, headers, rows2, widths=[18, 25, 45])

    def _create_benchmark_section(self, parent):
        """指標の目安セクション"""
        section = self._create_section_header(parent, "2. 指標の目安・業界水準")

        content = ttk.Frame(section)
        content.pack(fill=X, padx=10, pady=10)

        headers = ['指標', '製造業一般', '注意が必要な水準']
        rows = [
            ('売上総利益率', '20〜30%', '15%未満'),
            ('営業利益率', '3〜8%', '0%以下（赤字）'),
            ('経常利益率', '3〜7%', '0%以下（赤字）'),
            ('売上原価率', '70〜80%', '85%超'),
            ('販管費率', '15〜25%', '30%超'),
        ]
        self._create_table(content, headers, rows, widths=[18, 20, 20])

        ttk.Label(
            content,
            text="※業界・企業規模により異なるため、自社の過去データとの比較を重視してください",
            bootstyle="secondary",
            font=("", 9)
        ).pack(anchor=W, pady=(10, 0))

    def _create_chart_guide_section(self, parent):
        """グラフの見方セクション"""
        section = self._create_section_header(parent, "3. グラフの見方")

        content = ttk.Frame(section)
        content.pack(fill=X, padx=10, pady=10)

        guides = [
            ("■ 推移グラフ（折れ線グラフ）", [
                "・上昇トレンド: 右肩上がりは業績改善を示す",
                "・下降トレンド: 右肩下がりは業績悪化の兆候",
                "・急激な変動: 特殊要因（大型案件、一時的費用等）の可能性",
                "・季節変動: 毎年同時期に同様のパターンがあれば季節性",
            ]),
            ("■ 構成比グラフ（円グラフ・棒グラフ）", [
                "・構成比の変化: 前期比で大きく変動した項目に注目",
                "・偏り: 特定部門・項目への過度な依存はリスク要因",
                "・バランス: 複数の収益源がある状態が安定的",
            ]),
            ("■ 部門比較グラフ", [
                "・部門間格差: 大きな差がある場合、要因分析が必要",
                "・ベストプラクティス: 高収益部門の手法を他部門へ展開",
                "・改善ターゲット: 低収益部門の課題特定",
            ]),
        ]

        for title, items in guides:
            ttk.Label(
                content,
                text=title,
                font=("", 10, "bold")
            ).pack(anchor=W, pady=(10, 5))

            for item in items:
                ttk.Label(
                    content,
                    text=item,
                    wraplength=700
                ).pack(anchor=W, padx=(10, 0), pady=1)

    def _create_analysis_section(self, parent):
        """分析のポイントセクション"""
        section = self._create_section_header(parent, "4. 分析のポイント")

        content = ttk.Frame(section)
        content.pack(fill=X, padx=10, pady=10)

        analyses = [
            ("■ 時系列分析", [
                "1. トレンド把握: 3ヶ月以上の傾向を確認",
                "2. 前年同月比較: 季節要因を排除した比較",
                "3. 異常値の特定: 急激な変動の原因調査",
                "4. 先行指標: 売上は利益に先行することが多い",
            ]),
            ("■ 部門間比較", [
                "1. 収益性の差: なぜ差が生じているかを分析",
                "2. コスト構造: 原価・販管費の構成比較",
                "3. 改善余地: 低収益部門の改善ポイント特定",
            ]),
            ("■ 原価分析", [
                "1. 変動費vs固定費: 売上変動への感応度把握",
                "2. 材料費: 調達価格、歩留まりの確認",
                "3. 労務費: 生産性、残業時間の確認",
                "4. 外注費: 内製化の検討余地",
            ]),
        ]

        for title, items in analyses:
            ttk.Label(
                content,
                text=title,
                font=("", 10, "bold")
            ).pack(anchor=W, pady=(10, 5))

            for item in items:
                ttk.Label(
                    content,
                    text=item,
                    wraplength=700
                ).pack(anchor=W, padx=(10, 0), pady=1)

    def _create_action_section(self, parent):
        """改善アクションセクション"""
        section = self._create_section_header(parent, "5. 改善アクションへの繋げ方")

        content = ttk.Frame(section)
        content.pack(fill=X, padx=10, pady=10)

        headers = ['状況', '考えられる原因', '改善アクション例']
        rows = [
            ('売上総利益率低下', '材料費高騰、価格競争', '調達先見直し、価格転嫁、製品構成見直し'),
            ('営業利益率低下', '販管費増加', '固定費削減、業務効率化'),
            ('部門間で利益率格差', '案件特性、効率差', 'ベストプラクティス共有、人員配置見直し'),
            ('売上減少', '受注減、案件遅延', '営業強化、顧客開拓'),
            ('労務費率上昇', '生産性低下、残業増', '工程改善、設備投資、人員配置最適化'),
        ]
        self._create_table(content, headers, rows, widths=[18, 22, 35])

    def _create_glossary_section(self, parent):
        """用語集セクション"""
        section = self._create_section_header(parent, "6. 用語集")

        content = ttk.Frame(section)
        content.pack(fill=X, padx=10, pady=10)

        terms = [
            ('売上高', '企業の主たる営業活動から得られた収益の総額'),
            ('売上原価', '売上を得るために直接かかった費用（材料費、労務費、経費）'),
            ('売上総利益（粗利益）', '売上高から売上原価を差し引いた利益'),
            ('販売費及び一般管理費', '販売活動・管理活動にかかる費用（人件費、広告費、事務費等）'),
            ('営業利益', '売上総利益から販管費を差し引いた、本業での利益'),
            ('営業外収益', '本業以外から得られる収益（受取利息、配当金等）'),
            ('営業外費用', '本業以外でかかる費用（支払利息等）'),
            ('経常利益', '営業利益に営業外損益を加減した、経常的な活動による利益'),
            ('特別利益', '臨時的・例外的に発生した利益（固定資産売却益等）'),
            ('特別損失', '臨時的・例外的に発生した損失（固定資産除却損等）'),
            ('税引前当期利益', '経常利益に特別損益を加減した、税金控除前の利益'),
            ('当期利益（純利益）', '税金を差し引いた最終的な利益'),
            ('借方', '資産の増加・費用の発生を記録する側'),
            ('貸方', '負債・資本の増加・収益の発生を記録する側'),
            ('前残高', '前月末時点での累計残高'),
            ('残高', '当月末時点での累計残高'),
        ]

        for term, desc in terms:
            row_frame = ttk.Frame(content)
            row_frame.pack(fill=X, pady=2)

            ttk.Label(
                row_frame,
                text=f"【{term}】",
                font=("", 9, "bold"),
                width=22,
                anchor=W
            ).pack(side=LEFT)

            ttk.Label(
                row_frame,
                text=desc,
                wraplength=550
            ).pack(side=LEFT, padx=(5, 0))
