"""LotterySimulatorクラスのテストモジュール"""

import unittest
from unittest.mock import patch

from src.lottery.lottery_simulator import LotterySimulator


class TestLotterySimulator(unittest.TestCase):
    """LotterySimulatorクラスのテスト"""

    def setUp(self):
        """各テスト前の共通セットアップ"""
        self.total_attendance = 100000
        self.num_events = 10
        self.target_events = {"tokyo": 2, "osaka": 1}
        self.core_fan_population = 50000
        self.simulator = LotterySimulator(
            self.total_attendance,
            self.num_events,
            self.target_events,
            self.core_fan_population,
        )

    def test_init(self):
        """LotterySimulatorの初期化が正しく行われるかテスト"""
        self.assertEqual(self.simulator.total_overall_attendance, self.total_attendance)
        self.assertEqual(self.simulator.num_total_events, self.num_events)
        self.assertEqual(self.simulator.user_target_events_details, self.target_events)
        self.assertEqual(
            self.simulator.core_fan_total_population, self.core_fan_population
        )
        self.assertEqual(self.simulator.duplicate_当選_config, {})
        self.assertEqual(
            self.simulator.seats_per_event, self.total_attendance / self.num_events
        )
        self.assertEqual(self.simulator.user_total_target_events, 3)
        self.assertEqual(
            self.simulator.total_seats_for_user_events,
            (self.total_attendance / self.num_events) * 3,
        )
        self.assertEqual(self.simulator.stages, [])
        self.assertEqual(self.simulator.results_per_stage_raw, [])
        self.assertEqual(self.simulator.final_probabilities, {})
        self.assertEqual(self.simulator.total_weight, 0)

    def test_init_with_invalid_params(self):
        """不正なパラメータでの初期化時に例外が発生するかテスト"""
        with self.assertRaises(ValueError):
            LotterySimulator(
                self.total_attendance, 0, self.target_events, self.core_fan_population
            )
        with self.assertRaises(ValueError):
            LotterySimulator(
                self.total_attendance, self.num_events, {}, self.core_fan_population
            )

    def test_add_stage(self):
        """ステージの追加が正しく行われるかテスト"""
        self.simulator.add_stage("テスト1", 0.3, 1000, 5)
        self.assertEqual(len(self.simulator.stages), 1)
        self.assertEqual(self.simulator.stages[0].name, "テスト1")
        self.assertEqual(self.simulator.total_weight, 5)
        self.simulator.add_stage("テスト2", 0.5, 2000, 3)
        self.assertEqual(len(self.simulator.stages), 2)
        self.assertEqual(self.simulator.stages[1].name, "テスト2")
        self.assertEqual(self.simulator.total_weight, 8)

    def test_add_stage_with_invalid_params(self):
        """不正なパラメータでのステージ追加時に例外が発生するかテスト"""
        with self.assertRaises(ValueError):
            self.simulator.add_stage("テスト", 1.5, 1000, 5)
        with self.assertRaises(ValueError):
            self.simulator.add_stage("テスト", -0.1, 1000, 5)
        with self.assertRaises(ValueError):
            self.simulator.add_stage("テスト", 0.5, -100, 5)
        with self.assertRaises(ValueError):
            self.simulator.add_stage("テスト", 0.5, 1000, 0)

    def test_allocate_seats_to_stages(self):
        """座席配分が正しく行われるかテスト"""
        self.simulator.add_stage("テスト1", 0.3, 1000, 5)
        self.simulator.add_stage("テスト2", 0.5, 2000, 3)
        self.simulator.add_stage("テスト3", 0.7, 3000, 2)
        self.simulator._allocate_seats_to_stages()
        total_seats = self.simulator.total_seats_for_user_events
        total_weight = 10
        self.assertEqual(
            self.simulator.stages[0].allocated_seats_original,
            round(total_seats * (5 / total_weight)),
        )
        self.assertEqual(
            self.simulator.stages[1].allocated_seats_original,
            round(total_seats * (3 / total_weight)),
        )
        sum_allocated = sum(
            stage.allocated_seats_original for stage in self.simulator.stages
        )
        self.assertEqual(sum_allocated, round(total_seats))
        for stage in self.simulator.stages:
            self.assertEqual(
                stage.effective_seats_for_new_winners, stage.allocated_seats_original
            )

    def test_allocate_seats_with_duplicate_config(self):
        """重複当選設定がある場合の座席配分テスト"""
        simulator = LotterySimulator(
            self.total_attendance,
            self.num_events,
            self.target_events,
            self.core_fan_population,
            {"type": "seat_reduction", "rate": 0.2},
        )
        simulator.add_stage("テスト1", 0.3, 1000, 5)
        simulator.add_stage("テスト2", 0.5, 2000, 3)
        simulator._allocate_seats_to_stages()
        for stage in simulator.stages:
            self.assertEqual(
                stage.effective_seats_for_new_winners,
                round(stage.allocated_seats_original * 0.8),
            )

    def test_calculate_probabilities_no_stages(self):
        """ステージがない場合の確率計算テスト"""
        result = self.simulator.calculate_probabilities()
        self.assertEqual(len(result), 1)
        self.assertIn("全選考で落選", result)
        self.assertEqual(result["全選考で落選"], 1.0)

    def test_calculate_probabilities(self):
        """確率計算が正しく行われるかテスト"""
        simulator = LotterySimulator(10000, 10, {"test": 1}, 1000)
        simulator.add_stage("ステージ1", 0.5, 0, 1)
        simulator.add_stage("ステージ2", 1.0, 0, 1)
        result = simulator.calculate_probabilities()
        self.assertAlmostEqual(
            result["ステージ1で当選"], 1.0, places=2
        )  # 席1000, 申込500 -> 当選率100%
        self.assertAlmostEqual(
            result["ステージ2で当選"], 0.0, places=2
        )  # ステージ1で全員当選
        self.assertAlmostEqual(result["全選考で落選"], 0.0, places=2)
        self.assertAlmostEqual(sum(result.values()), 1.0, places=2)

    def test_calculate_probabilities_with_duplicate(self):
        """重複当選設定がある場合の確率計算テスト"""
        simulator = LotterySimulator(
            10000, 10, {"test": 1}, 1000, {"type": "seat_reduction", "rate": 0.2}
        )
        simulator.add_stage(
            "ステージ1", 0.5, 0, 1
        )  # 席500*0.8=400, 申込500 -> 当選率0.8
        simulator.add_stage(
            "ステージ2", 1.0, 0, 1
        )  # 席500*0.8=400, 申込(1000-400)=600 -> 当選率400/600
        result = simulator.calculate_probabilities()

        # ステージ1: 席(1000/2)*0.8 = 400. 申込者 1000*0.5 = 500. 当選者 min(400,500)=400. 条件付当選率 400/500 = 0.8.
        #           ステージ1当選確率 = 1.0 * 0.8 = 0.8
        self.assertAlmostEqual(result["ステージ1で当選"], 0.8, places=3)

        # ステージ2: 席(1000/2)*0.8 = 400.
        #           前提申込者 1000*1.0 = 1000.
        #           実質申込者 1000 - 400(ステージ1当選者) = 600.
        #           当選者 min(400,600)=400. 条件付当選率 400/600 = 0.666...
        #           ステージ2当選確率 = (1.0 - 0.8) * (400/600) = 0.2 * 0.666... = 0.1333...
        self.assertAlmostEqual(result["ステージ2で当選"], 0.1333, places=3)

        # 全選考で落選: (1.0 - 0.8) * (1 - 400/600) = 0.2 * (200/600) = 0.2 * 0.333... = 0.0666...
        self.assertAlmostEqual(result["全選考で落選"], 0.0666, places=3)

        self.assertAlmostEqual(sum(result.values()), 1.0, places=3)

    @patch("builtins.print")
    def test_display_results(self, mock_print):
        """結果表示が正しく行われるかテスト"""
        simulator = LotterySimulator(10000, 10, {"test": 1}, 1000)
        simulator.add_stage("ステージ1", 0.5, 0, 1)
        simulator.calculate_probabilities()
        simulator.display_results()
        self.assertTrue(mock_print.called)

        mock_print.reset_mock()
        simulator.display_results(display_details=True)
        # 詳細表示ではより多くのprintが呼ばれるはず
        # 具体的な呼び出し回数は実装に依存するが、最低でも基本表示より多いことを確認
        self.assertTrue(mock_print.call_count > 5)  # 以前のテストより具体的な値


if __name__ == "__main__":
    unittest.main()
