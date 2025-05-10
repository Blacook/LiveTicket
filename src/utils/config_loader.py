"""設定ファイル読み込み関連のモジュール"""

import json


def load_config(config_path: str = "config/config.json") -> dict:
    """設定ファイルを読み込む関数

    指定されたJSONファイルを読み込み、シミュレーションの設定を取得します。
    ファイルが見つからない場合やJSONフォーマットが不正な場合はエラーメッセージを
    表示し、Noneを返します。

    Args:
        config_path (str, optional): 設定ファイルのパス。デフォルトは"config.json"

    Returns:
        dict or None: 設定内容を含む辞書。エラーが発生した場合はNone
    """
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        print(f"設定ファイル '{config_path}' を読み込みました")
        return config
    except FileNotFoundError:
        print(f"エラー: 設定ファイル '{config_path}' が見つかりません")
        return {}
    except json.JSONDecodeError as e:
        print(f"エラー: 設定ファイル '{config_path}' のJSONフォーマットが不正です: {e}")
        return {}
    except Exception as e:
        print(
            f"エラー: 設定ファイル '{config_path}' の読み込み中に問題が発生しました: {e}"
        )
        return {}
