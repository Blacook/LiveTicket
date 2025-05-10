"""plotterモジュールのテスト"""

import unittest
from unittest.mock import MagicMock, patch

from src.utils.plotter import plot_probability_comparison


class TestPlotProbabilityComparison(unittest.TestCase):
    """plot_probability_comparison関数のテスト"""

    @patch("src.utils.plotter.plt.show")
    @patch("src.utils.plotter.plt.subplots")
    def test_plot_probability_comparison(
        self, mock_subplots: MagicMock, mock_show: MagicMock
    ) -> None:
        """グラフ描画が正しく行われるかテスト"""
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        results_list = [
            {"ステージ1で当選": 0.8, "ステージ2で当選": 0.15, "全選考で落選": 0.05},
            {"ステージ1で当選": 0.7, "ステージ2で当選": 0.2, "全選考で落選": 0.1},
        ]
        case_names = ["ケース1", "ケース2"]
        stage_map = {
            "ステージ1で当選": "S1",
            "ステージ2で当選": "S2",
            "全選考で落選": "Lose",
        }

        plot_probability_comparison(results_list, case_names, stage_map)

        self.assertTrue(mock_subplots.called)
        self.assertTrue(mock_ax.bar.called)
        self.assertTrue(mock_ax.set_ylabel.called)
        self.assertTrue(mock_ax.set_title.called)
        self.assertTrue(mock_ax.set_xticks.called)
        self.assertTrue(mock_ax.set_xticklabels.called)
        self.assertTrue(mock_ax.legend.called)
        self.assertTrue(mock_show.called)

    @patch("builtins.print")
    def test_plot_probability_comparison_invalid_input(
        self, mock_print: MagicMock
    ) -> None:
        """不正な入力でのグラフ描画テスト"""
        plot_probability_comparison([], [])
        mock_print.assert_called_with("描画データまたはケース名が不適切です。")
        plot_probability_comparison([{}], ["ケース1", "ケース2"])
        mock_print.assert_called_with("描画データまたはケース名が不適切です。")


if __name__ == "__main__":
    unittest.main()
