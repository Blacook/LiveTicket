"""グラフ描画関連のモジュール"""

import re
from typing import Dict, List, Optional, Tuple

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


def plot_probability_comparison(
    results_list: List[Dict[str, float]],
    case_names_list: List[str],
    stage_name_map: Optional[Dict[str, str]] = None,
) -> None:
    """複数のシミュレーション結果を積み上げ横棒グラフで比較して表示する。

    各ケース（条件パターン）をY軸に、各選考ステージの確率を積み上げてX軸に表示します。
    各積み上げ棒の合計は100%になります。

    Args:
        results_list (list of dict): 各ケースのfinal_probabilities辞書のリスト。
            各辞書は {"ステージ名で当選": float, ...} の形式。
        case_names_list (list of str): 各ケースの名前のリスト。
            例: ["重複当選なし", "重複当選あり (新規枠10%減)"]
        stage_name_map (dict, optional): final_probabilitiesのキーとグラフ表示名のマッピング。
            例: {"1次(CD+年会員)で当選": "1次", "全選考で落選": "全滅"}

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

    def get_sort_key(key_str: str) -> Tuple[int, int, str]:
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
    num_cases = len(case_names_list)
    y_positions = np.arange(num_cases)
    bar_height = 0.6  # 各積み上げ棒の高さ

    fig, ax = plt.subplots(
        figsize=(12, max(6, num_cases * 0.8))
    )  # ケース数に応じて高さを調整

    # ステージごとの色を定義
    prop_cycle = plt.rcParams["axes.prop_cycle"]
    default_colors = prop_cycle.by_key()["color"]
    stage_colors = {
        key: default_colors[i % len(default_colors)]
        for i, key in enumerate(internal_keys_ordered)
    }

    for i, case_name in enumerate(case_names_list):
        case_results = results_list[i]
        left_offset = 0
        for stage_idx, stage_key in enumerate(internal_keys_ordered):
            probability = case_results.get(stage_key, 0) * 100
            display_name_for_legend = display_names_ordered[stage_idx]

            if probability > 0:  # 確率が0より大きい場合のみ描画
                ax.barh(
                    y_positions[i],
                    probability,
                    height=bar_height,
                    left=left_offset,
                    color=stage_colors[stage_key],
                    label=(
                        display_name_for_legend if i == 0 else None
                    ),  # 凡例には最初のケースの分だけ追加
                    edgecolor="white",
                )
                # セグメント内にテキスト表示 (任意、見づらい場合は調整または削除)
                if probability > 3:  # 小さすぎるセグメントにはテキストを表示しない
                    ax.text(
                        left_offset + probability / 2,
                        y_positions[i],
                        f"{probability:.1f}%",
                        ha="center",
                        va="center",
                        color=(
                            "white" if probability > 10 else "black"
                        ),  # 背景色に応じて文字色変更
                        fontsize=7,
                    )
            left_offset += probability

    ax.set_xlabel("確率 (%)", fontsize=12)
    ax.set_ylabel("シミュレーションケース", fontsize=12)
    ax.set_title("各ケースにおける選考ステージ別当選確率の積み上げ", fontsize=14)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(case_names_list, fontsize=10)
    ax.set_xlim(0, 100)  # X軸の範囲を0-100%に固定

    # 凡例の重複を削除して表示
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(
        zip(labels, handles)
    )  # collections.OrderedDict だとなお良いが、標準ライブラリで
    ax.legend(
        by_label.values(),
        by_label.keys(),
        title="選考ステージ",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        fontsize=9,
    )

    ax.grid(axis="y", linestyle="--", alpha=0.7)
    fig.tight_layout(rect=[0, 0, 0.85, 1])  # 凡例スペースを考慮
    plt.show()
