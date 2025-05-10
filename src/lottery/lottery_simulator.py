"""LotterySimulatorクラスの定義モジュール"""

from .lottery_stage import LotteryStage


class LotterySimulator:
    """当選確率シミュレータークラス。

    このクラスは、複数の選考ステージにおける当選確率をシミュレートするための
    メインクラスです。各ステージの申込者数、当選者数、確率などを計算します。

    Attributes:
        total_overall_attendance (int): 全公演の総動員数
        num_total_events (int): 全公演数
        user_target_events_details (dict): ユーザーが申し込む公演の詳細（地域ごとの公演数）
        core_fan_total_population (int): コアファンの総人口
        duplicate_当選_config (dict): 重複当選の設定（type, rateなど）
        stages (list): 追加された選考ステージのリスト
        total_weight (float): 全ステージの重み合計
        seats_per_event (float): 1公演あたりの座席数
        user_total_target_events (int): ユーザーが申し込む公演の総数
        total_seats_for_user_events (float): ユーザーが申し込む公演の総座席数
        results_per_stage_raw (list): 各ステージの計算結果
        final_probabilities (dict): 最終的な当選確率の内訳
    """

    def __init__(
        self,
        total_overall_attendance: int,
        num_total_events: int,
        user_target_events_details: dict,
        core_fan_total_population: int,
        duplicate_当選_config: dict = {},
    ) -> None:
        """LotterySimulatorクラスの初期化メソッド

        Args:
            total_overall_attendance (int): 全公演の総動員数
            num_total_events (int): 全公演数
            user_target_events_details (dict): ユーザーが申し込む公演の詳細（地域ごとの公演数）
            core_fan_total_population (int): コアファンの総人口
            duplicate_当選_config (dict, optional): 重複当選の設定。デフォルトはNone
                例: {"type": "seat_reduction", "rate": 0.1} - 新規当選枠を10%減らす設定

        Raises:
            ValueError: 総公演数またはユーザーが申し込む公演数が0以下の場合
        """
        self.total_overall_attendance = total_overall_attendance
        self.num_total_events = num_total_events
        self.user_target_events_details = user_target_events_details
        self.core_fan_total_population = core_fan_total_population
        self.duplicate_当選_config = (
            duplicate_当選_config if duplicate_当選_config else {}
        )
        self.stages = []
        self.total_weight = 0
        if self.num_total_events <= 0:
            raise ValueError("総公演数は0より大きい値である必要があります。")
        self.seats_per_event = self.total_overall_attendance / self.num_total_events
        self.user_total_target_events = sum(self.user_target_events_details.values())
        if self.user_total_target_events <= 0:
            raise ValueError(
                "ユーザーが申し込む公演数は0より大きい値である必要があります。"
            )
        self.total_seats_for_user_events = (
            self.seats_per_event * self.user_total_target_events
        )
        self.results_per_stage_raw = []
        self.final_probabilities = {}

    def add_stage(
        self,
        name: str,
        applicant_core_fan_ratio: float,
        additional_applicants: int,
        weight: float,
    ) -> None:
        """選考ステージを追加するメソッド

        Args:
            name (str): ステージの名前
            applicant_core_fan_ratio (float): このステージで申し込むコアファンの割合（0.0〜1.0）
            additional_applicants (int): コアファン以外の追加申込者数
            weight (float): 座席配分の重み付け係数

        Raises:
            ValueError: パラメータが不正な値の場合（申込割合が0-1の範囲外、追加申込者数が負、比重が0以下）
        """
        if not (0.0 <= applicant_core_fan_ratio <= 1.0):
            raise ValueError(
                f"ステージ「{name}」のコアファン申込割合は0.0から1.0の間である必要があります。"
            )
        if additional_applicants < 0:
            raise ValueError(
                f"ステージ「{name}」の追加申込者数は0以上である必要があります。"
            )
        if weight <= 0:
            raise ValueError(
                f"ステージ「{name}」の比重は0より大きい値である必要があります。"
            )
        stage = LotteryStage(
            name, applicant_core_fan_ratio, additional_applicants, weight
        )
        self.stages.append(stage)
        self.total_weight += weight

    def _allocate_seats_to_stages(self) -> None:
        """各選考ステージに座席を配分する内部メソッド

        各ステージの重みに基づいて座席を配分し、重複当選の設定がある場合は
        新規当選者向けの有効座席数を計算します。

        Raises:
            ValueError: ステージが追加されているが比重の合計が0の場合、または
                       座席減少率が0.0から1.0の範囲外の場合
        """
        if self.total_weight == 0 and self.stages:
            raise ValueError("選考ステージが追加されていますが、比重の合計が0です。")
        if not self.stages:
            return

        running_allocated_sum = 0
        for i, stage in enumerate(self.stages):
            if i < len(self.stages) - 1:
                seats = round(
                    self.total_seats_for_user_events
                    * (stage.weight / self.total_weight)
                )
            else:
                seats = round(self.total_seats_for_user_events - running_allocated_sum)
            stage.allocated_seats_original = seats
            running_allocated_sum += seats

        reduction_rate = 0.0
        if self.duplicate_当選_config.get("type") == "seat_reduction":
            reduction_rate = self.duplicate_当選_config.get("rate", 0.0)
            if not (0.0 <= reduction_rate <= 1.0):
                raise ValueError("座席減少率は0.0から1.0の間である必要があります。")
        for stage in self.stages:
            stage.effective_seats_for_new_winners = round(
                stage.allocated_seats_original * (1 - reduction_rate)
            )

    def calculate_probabilities(self) -> dict:
        """各選考ステージの当選確率を計算するメソッド

        各ステージの申込者数、当選者数、条件付き当選確率を計算し、
        最終的な当選確率の内訳を計算します。前のステージで当選した人は
        次のステージには申し込まないという前提で計算します。

        Returns:
            dict: 最終的な当選確率の内訳（各ステージでの当選確率と全選考で落選する確率）
        """
        if not self.stages:
            self.final_probabilities = {"全選考で落選": 1.0}
            return self.final_probabilities

        self._allocate_seats_to_stages()
        cumulative_new_winners = 0
        prob_of_reaching_stage_unwon = 1.0
        self.results_per_stage_raw = []
        self.final_probabilities = {}

        for stage in self.stages:
            potential_core_fan_applicants = round(
                self.core_fan_total_population * stage.applicant_core_fan_ratio
            )
            stage.premise_applicants_for_stage_type = (
                potential_core_fan_applicants + stage.additional_applicants
            )
            stage.actual_applicants_for_stage = max(
                0, stage.premise_applicants_for_stage_type - cumulative_new_winners
            )

            if (
                stage.actual_applicants_for_stage == 0
                or stage.effective_seats_for_new_winners == 0
            ):
                stage.conditional_win_prob_in_stage = 0.0
                stage.winners_in_stage = 0
            else:
                stage.winners_in_stage = min(
                    stage.actual_applicants_for_stage,
                    stage.effective_seats_for_new_winners,
                )
                stage.conditional_win_prob_in_stage = (
                    stage.winners_in_stage / stage.actual_applicants_for_stage
                )

            prob_win_first_time_at_this_stage = (
                prob_of_reaching_stage_unwon * stage.conditional_win_prob_in_stage
            )
            self.final_probabilities[f"{stage.name}で当選"] = (
                prob_win_first_time_at_this_stage
            )
            prob_of_reaching_stage_unwon *= 1 - stage.conditional_win_prob_in_stage
            cumulative_new_winners += stage.winners_in_stage
            self.results_per_stage_raw.append(stage)
        self.final_probabilities["全選考で落選"] = prob_of_reaching_stage_unwon

        return self.final_probabilities

    def display_results(self, display_details: bool = False) -> None:
        """シミュレーション結果を表示するメソッド

        計算された当選確率や各ステージの詳細情報をコンソールに表示します。

        Args:
            display_details (bool, optional): 各ステージの詳細情報を表示するかどうか。デフォルトはFalse
        """
        print("\n--- 当選確率シミュレーション結果 ---")
        print(
            f"ユーザーが申し込む公演の総当選枠（理論値）: {self.total_seats_for_user_events:.0f}席"
        )
        if self.duplicate_当選_config.get("type") == "seat_reduction":
            rate = self.duplicate_当選_config.get("rate", 0.0) * 100
            print(
                f"重複当選考慮: 新規当選者向け有効枠が各ステージで {rate:.1f}% 減少すると仮定"
            )
        else:
            print("重複当選考慮: なし (または未設定)")

        if display_details and self.results_per_stage_raw:
            print("\n--- 各選考ステージ詳細 ---")
            header = f"{'選考名':<12} | {'割当席(元)':>8} | {'有効席(新)':>8} | {'前提申込者':>10} | {'実質申込者':>10} | {'当選者数':>8} | {'条件付当選率':>10}"
            print(header)
            print("-" * len(header))
            total_potential_seats_sum, total_effective_seats_sum, total_winners_sum = (
                0,
                0,
                0,
            )
            for r in self.results_per_stage_raw:
                print(
                    f"{r.name:<12} | {r.allocated_seats_original:>8} | {r.effective_seats_for_new_winners:>8} | {r.premise_applicants_for_stage_type:>10} | {r.actual_applicants_for_stage:>10} | {r.winners_in_stage:>8} | {r.conditional_win_prob_in_stage*100:>9.2f}%"
                )
                total_potential_seats_sum += r.allocated_seats_original
                total_effective_seats_sum += r.effective_seats_for_new_winners
                total_winners_sum += r.winners_in_stage
            print("-" * len(header))
            print(
                f"{'合計':<12} | {total_potential_seats_sum:>8} | {total_effective_seats_sum:>8} | {'':>10} | {'':>10} | {total_winners_sum:>8} |"
            )

        print("\n--- 最終的な当選確率の内訳 (全事象100%) ---")
        if not self.final_probabilities:
            print("計算結果がありません。")
            return
        for event, probability in self.final_probabilities.items():
            print(f"{event}: {probability*100:.2f}%")
        sum_probs_display = sum(self.final_probabilities.values()) * 100
        print(
            f"合計: {sum_probs_display:.2f}% (計算上の丸め誤差により100%からわずかにずれることがあります)"
        )
        print("------------------------------------")
