"""config_loaderモジュールのテスト"""

import json
import os
import tempfile
import unittest
from unittest.mock import patch

from src.utils.config_loader import load_config


class TestLoadConfig(unittest.TestCase):
    """load_config関数のテスト"""

    def setUp(self):
        self.test_config_data = {
            "simulation_settings": {"total_overall_attendance": 10000},
            "user_target_events_details": {"test": 1},
            "lottery_stages_definition": [{"name": "ステージ1"}],
            "simulation_cases_to_run": [{"case_name": "テストケース"}],
        }
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.temp_dir.name, "test_config.json")
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.test_config_data, f)

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch("builtins.print")
    def test_load_config_success(self, mock_print):
        """設定ファイルの読み込みが成功するかテスト"""
        config = load_config(self.config_path)
        self.assertIsNotNone(config)
        self.assertEqual(
            config["simulation_settings"]["total_overall_attendance"], 10000
        )
        mock_print.assert_called_with(
            f"設定ファイル '{self.config_path}' を読み込みました"
        )

    @patch("builtins.print")
    def test_load_config_file_not_found(self, mock_print):
        """存在しないファイルの読み込み時のテスト"""
        config = load_config("non_existent_file.json")
        self.assertEqual(config, {})
        mock_print.assert_called_with(
            "エラー: 設定ファイル 'non_existent_file.json' が見つかりません"
        )

    @patch("builtins.print")
    def test_load_config_invalid_json(self, mock_print):
        """不正なJSONファイルの読み込み時のテスト"""
        invalid_json_path = os.path.join(self.temp_dir.name, "invalid.json")
        with open(invalid_json_path, "w", encoding="utf-8") as f:
            f.write("{不正なJSON")
        config = load_config(invalid_json_path)
        self.assertEqual(config, {})
        self.assertTrue(
            mock_print.call_args[0][0].startswith(
                f"エラー: 設定ファイル '{invalid_json_path}' のJSONフォーマットが不正です:"
            )
        )

    @patch("builtins.print")
    def test_load_config_generic_exception(self, mock_print):
        """その他の例外発生時のテスト"""
        with patch("builtins.open", side_effect=Exception("Test general error")):
            config = load_config(self.config_path)
            self.assertEqual(config, {})
            self.assertTrue(
                mock_print.call_args[0][0].startswith(
                    f"エラー: 設定ファイル '{self.config_path}' の読み込み中に問題が発生しました:"
                )
            )


if __name__ == "__main__":
    unittest.main()
