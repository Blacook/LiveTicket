"""グラフ描画関連のモジュール"""

import re

import matplotlib.pyplot as plt
import numpy as np

# matplotlibで日本語が文字化けする場合の対策
try:
    plt.rcParams["font.sans-serif"] = [
        "Hiragino Sans",
        "Yu Gothic",
        "Meirio",
        "TakaoPGothic",
        "Noto Sans CJK JP",
        "IPAexGothic",  # Added for broader compatibility
    ]
    plt.rcParams["axes.unicode_minus"] = False  # マイナス記号の文字化け対策
except Exception:
    print(
        "日本語フォントの設定に失敗しました。グラフの日本語が文字化けする可能性があります。"
    )


def plot_probability_comparison(results_list, case_names_list, stage_name_map=None):
    """複数のシミュレーション結果をグループ化された棒グラフで比較して表示する。

    各ケースの当選確率を並べて表示し、視覚的に比較できるようにします。
    グラフのX軸には各選考ステージ、Y軸には確率（%）が表示されます。

    Args:
        results_list (list of dict): 各ケースのfinal_probabilities辞書のリスト。
            各辞書は {"ステージ名で当選": 確率, ...} の形式。
        case_names_list (list of str): 各ケースの名前のリスト。
            例: ["重複当選なし", "重複当選あり (新規枠10%減)"]
        stage_name_map (dict, optional): final_probabilitiesのキーとグラフ表示名のマッピング。
            例: {"1次(CD+年会員)で当選": "1次", ...}

    Returns:
        None: グラフを表示するのみで、戻り値はありません。
    """
    if (
        not results_list
        or not case_names_list
        or len(results_list) != len(case_names_list)
    ):
        print("描画データまたはケース名が不適切です。")
        return

    sample_result = results_list[0]

    def get_sort_key(key_str):
        match = re.match(r"(\d+)次", key_str)
        if match:
            return (0, int(match.group(1)), key_str)
        if "落選" in key_str or "全滅" in key_str:  # "全滅"も考慮
            return (1, 0, key_str)
        return (2, 0, key_str)

    sorted_dict_keys = sorted(sample_result.keys(), key=get_sort_key)

    if stage_name_map:
        display_names_ordered = [
            stage_name_map.get(k, k.replace("で当選", "")) for k in sorted_dict_keys
        ]
        internal_keys_ordered = (
            sorted_dict_keys  # Use all keys from sample for data extraction
        )
    else:
        display_names_ordered = [k.replace("で当選", "") for k in sorted_dict_keys]
        internal_keys_ordered = sorted_dict_keys

    num_categories = len(display_names_ordered)
    num_cases = len(results_list)
    x = np.arange(num_categories)
    width = 0.8 / num_cases

    fig, ax = plt.subplots(figsize=(max(12, num_categories * num_cases * 0.5 + 2), 7))

    for i, (case_results, case_name) in enumerate(zip(results_list, case_names_list)):
        probabilities = [
            case_results.get(internal_key, 0) * 100
            for internal_key in internal_keys_ordered
        ]
        bar_positions = x - (width * num_cases / 2) + (i * width) + (width / 2)
        rects = ax.bar(bar_positions, probabilities, width, label=case_name)
        ax.bar_label(rects, fmt="%.1f%%", padding=3, fontsize=8)

    ax.set_ylabel("確率 (%)", fontsize=12)
    ax.set_title("各選考ステージでの当選確率と比較", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(display_names_ordered, rotation=30, ha="right", fontsize=10)
    ax.legend(fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    fig.tight_layout()
    plt.show()
