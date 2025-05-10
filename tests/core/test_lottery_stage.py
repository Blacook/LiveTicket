"""LotteryStageクラスのテストモジュール"""

import unittest

from src.lottery.lottery_stage import LotteryStage


class TestLotteryStage(unittest.TestCase):
    """LotteryStageクラスのテスト"""

    def test_init(self):
        """LotteryStageの初期化が正しく行われるかテスト"""
        stage = LotteryStage("テスト", 0.5, 1000, 3)

        # 初期化パラメータが正しく設定されているか確認
        self.assertEqual(stage.name, "テスト")
        self.assertEqual(stage.applicant_core_fan_ratio, 0.5)
        self.assertEqual(stage.additional_applicants, 1000)
        self.assertEqual(stage.weight, 3)

        # 初期値が正しく設定されているか確認
        self.assertEqual(stage.allocated_seats_original, 0)
        self.assertEqual(stage.effective_seats_for_new_winners, 0)
        self.assertEqual(stage.premise_applicants_for_stage_type, 0)
        self.assertEqual(stage.actual_applicants_for_stage, 0)
        self.assertEqual(stage.winners_in_stage, 0)
        self.assertEqual(stage.conditional_win_prob_in_stage, 0.0)


if __name__ == "__main__":
    unittest.main()
