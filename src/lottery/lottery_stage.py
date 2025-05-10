"""LotteryStageクラスの定義モジュール"""


class LotteryStage:
    """各選考ステージの情報を保持するクラス。

    このクラスは、抽選の各ステージに関する情報（名前、申込者数、当選者数など）を
    保持し、シミュレーション計算のために使用されます。

    Attributes:
        name (str): ステージの名前（例: "1次(CD+年会員)"）
        applicant_core_fan_ratio (float): このステージで申し込むコアファンの割合（0.0〜1.0）
        additional_applicants (int): コアファン以外の追加申込者数
        weight (float): 座席配分の重み付け係数
        allocated_seats_original (int): このステージに割り当てられた席数（元の計算値）
        effective_seats_for_new_winners (int): 新規当選者向けの有効席数（重複当選考慮後）
        premise_applicants_for_stage_type (int): このステージの前提となる申込者数（理論値）
        actual_applicants_for_stage (int): 実際の申込者数（前ステージでの当選者を除く）
        winners_in_stage (int): このステージでの当選者数
        conditional_win_prob_in_stage (float): このステージでの条件付き当選確率
    """

    def __init__(
        self,
        name: str,
        applicant_core_fan_ratio: float,
        additional_applicants: int,
        weight: float,
    ) -> None:
        """LotteryStageクラスの初期化メソッド

        Args:
            name (str): ステージの名前
            applicant_core_fan_ratio (float): このステージで申し込むコアファンの割合（0.0〜1.0）
            additional_applicants (int): コアファン以外の追加申込者数
            weight (float): 座席配分の重み付け係数
        """
        self.name = name
        self.applicant_core_fan_ratio = applicant_core_fan_ratio
        self.additional_applicants = additional_applicants
        self.weight = weight
        self.allocated_seats_original = 0
        self.effective_seats_for_new_winners = 0
        self.premise_applicants_for_stage_type = 0
        self.actual_applicants_for_stage = 0
        self.winners_in_stage = 0
        self.conditional_win_prob_in_stage = 0.0
