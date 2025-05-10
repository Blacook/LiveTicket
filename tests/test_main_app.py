"""src.__main__ モジュールのテスト"""

import unittest
from unittest.mock import MagicMock, patch

from src.__main__ import (
    run_and_collect_results,  # main関数は直接テストせず、run_and_collect_resultsをテスト
)


class TestRunAndCollectResults(unittest.TestCase):
    """run_and_collect_results関数のテスト"""

    def setUp(self):
        """各テスト前の共通セットアップ"""
        self.simulation_settings = {
            "total_overall_attendance": 10000,
            "num_total_events": 10,
            "core_fan_total_population": 1000,
        }
        self.user_target_events_details = {"test": 1}
        self.stages_def = [("ステージ1", 0.5, 0, 1)]
        self.expected_result_dict = {"テスト結果": 1.0}

    # LotterySimulatorは __main__ モジュール内で core.lottery_simulator からインポートされるため、
    # __main__ の名前空間でパッチする
    @patch("src.__main__.LotterySimulator")
    @patch("builtins.print")  # display_results内のprintも抑制
    def test_run_and_collect_results_success(self, mock_print, mock_simulator_class):
        """シミュレーション実行が正しく行われるかテスト"""
        mock_simulator_instance = MagicMock()
        mock_simulator_class.return_value = mock_simulator_instance
        mock_simulator_instance.calculate_probabilities.return_value = (
            self.expected_result_dict
        )
        # display_resultsが呼ばれることを確認するためにfinal_probabilitiesも設定
        mock_simulator_instance.final_probabilities = self.expected_result_dict

        result = run_and_collect_results(
            self.simulation_settings,
            self.user_target_events_details,
            {},  # duplicate_config
            "テストケース",
            self.stages_def,
        )

        mock_simulator_class.assert_called_with(
            self.simulation_settings["total_overall_attendance"],
            self.simulation_settings["num_total_events"],
            self.user_target_events_details,
            self.simulation_settings["core_fan_total_population"],
            {},  # duplicate_config
        )
        mock_simulator_instance.add_stage.assert_called_with(*self.stages_def[0])
        self.assertTrue(mock_simulator_instance.calculate_probabilities.called)
        self.assertTrue(mock_simulator_instance.display_results.called)
        self.assertEqual(result, self.expected_result_dict)

    @patch("src.__main__.LotterySimulator")
    @patch("builtins.print")
    def test_run_and_collect_results_with_value_error(
        self, mock_print, mock_simulator_class
    ):
        """LotterySimulatorでのValueError発生時のテスト"""
        mock_simulator_instance = MagicMock()
        mock_simulator_class.return_value = mock_simulator_instance
        mock_simulator_instance.add_stage.side_effect = ValueError("テスト設定エラー")

        result = run_and_collect_results(
            self.simulation_settings,
            self.user_target_events_details,
            {},
            "エラーケース",
            self.stages_def,
        )
        self.assertIsNone(result)
        mock_print.assert_any_call("設定エラー (エラーケース): テスト設定エラー")


if __name__ == "__main__":
    unittest.main()
