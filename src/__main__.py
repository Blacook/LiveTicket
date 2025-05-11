"""コンサートチケット抽選シミュレーターのメイン実行モジュール"""

from typing import Any, Dict, List, Optional, Tuple

from .lottery.lottery_simulator import LotterySimulator
from .utils.config_loader import load_config
from .utils.plotter import plot_probability_comparison


def run_and_collect_results(
    simulation_settings: Dict[str, Any],
    user_target_events_details: Dict[str, int],
    duplicate_config: Dict[str, Any],
    case_name: str,
    stages_def: List[Tuple[str, float, int, float]],
) -> Optional[Dict[str, float]]:
    """シミュレーションを実行し結果を収集する関数

    指定された設定でシミュレーターを初期化し、計算を実行して結果を返します。
    エラーが発生した場合はエラーメッセージを表示し、Noneを返します。

    Args:
        simulation_settings (dict): シミュレーションの基本設定
        user_target_events_details (Dict[str, int]): ユーザーが申し込む公演の詳細
        duplicate_config (Dict[str, Any]): 重複当選の設定
        case_name (str): シミュレーションケースの名前（ログ表示用）
        stages_def (List[Tuple[str, float, int, float]]): 各選考ステージの定義のリスト
            各要素は (name: str, applicant_core_fan_ratio: float, additional_applicants: int, weight: float) の形式

    Returns:
        dict or None: 計算された当選確率の内訳。エラーが発生した場合はNone
    """

    try:
        simulator = LotterySimulator(
            simulation_settings["total_overall_attendance"],
            simulation_settings["num_total_events"],
            user_target_events_details,
            simulation_settings["core_fan_total_population"],
            duplicate_config,
        )
        for stage_args in stages_def:
            simulator.add_stage(*stage_args)

        simulator.calculate_probabilities()
        simulator.display_results(display_details=False)
        return simulator.final_probabilities
    except ValueError as e:
        print(f"設定エラー ({case_name}): {e}")
        return None
    except Exception as e:
        print(f"予期せぬエラー ({case_name}): {e}")
        return None


def main() -> None:
    """メイン処理"""
    config = load_config()  # config.jsonをデフォルトで読み込む
    if not config:
        print("設定ファイルの読み込みに失敗しました。プログラムを終了します。")
        return

    simulation_settings = config["simulation_settings"]
    user_target_events_details = config["user_target_events_details"]
    lottery_stages_config = config["lottery_stages_definition"]
    simulation_cases_config = config["simulation_cases_to_run"]

    # 前提条件の表示
    print("\n===== Simulation Settings =====")
    total_attendance = simulation_settings.get("total_overall_attendance", 0)
    num_events = simulation_settings.get("num_total_events", 1)  # 0除算を避ける
    core_fan_population = simulation_settings.get("core_fan_total_population", 0)

    print(f"全公演総動員数: {total_attendance:,} 人")
    print(f"全公演数: {num_events} 公演")
    if num_events > 0:
        seats_per_event = total_attendance / num_events
        print(f"1公演あたりの平均座席数: {seats_per_event:,.0f} 席")
    else:
        print("1公演あたりの平均座席数: 計算不可 (公演数が0)")
    print(f"コアファン総人口: {core_fan_population:,} 人")

    user_total_target_events = sum(user_target_events_details.values())
    details_str = ", ".join(
        [f"{region}: {count}" for region, count in user_target_events_details.items()]
    )
    print(f"ユーザーが申し込む公演数: {user_total_target_events} 公演 ({details_str})")
    print("--------------------------")

    stages_definition_list = [
        (
            stage["name"],
            stage["applicant_core_fan_ratio"],
            stage["additional_applicants"],
            stage["weight"],
        )
        for stage in lottery_stages_config
    ]

    stage_name_mapping_for_plot = {
        f"{stage['name']}で当選": stage[
            "name"
        ]  # Use the full stage name for the legend
        for stage in lottery_stages_config
    }
    stage_name_mapping_for_plot["全選考で落選"] = "全滅"

    all_results_for_plotting = []
    all_case_names_for_plotting = []

    for case_config in simulation_cases_config:
        case_name = case_config["case_name"]
        duplicate_config = case_config["duplicate_config"]

        print(f"\n===== Simulation Case: {case_name} =====")
        results = run_and_collect_results(
            simulation_settings,
            user_target_events_details,
            duplicate_config,
            case_name,
            stages_definition_list,
        )

        if results:
            all_results_for_plotting.append(results)
            all_case_names_for_plotting.append(case_name)

    if len(all_results_for_plotting) >= 2:
        plot_probability_comparison(
            all_results_for_plotting,
            all_case_names_for_plotting,
            stage_name_mapping_for_plot,
        )
    elif all_results_for_plotting:
        print(
            "\n1つのケースのみ計算されたため、比較グラフは表示しません。単独のグラフ描画は未実装です。"
        )
    else:
        print("\n描画するデータがありませんでした。")


if __name__ == "__main__":
    main()
