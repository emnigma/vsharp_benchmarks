import pandas as pd

from compare_configs import COMPARE_CONFS
from src.comparator import Color, Comparator, Strategy


def main():
    nn_res_path = "AI_all_new.csv"
    heuristic_res_path = "ExecutionTreeContributedCoverage_all.csv"

    nn_df = pd.read_csv(nn_res_path)
    heu_df = pd.read_csv(heuristic_res_path)

    comparator = Comparator(
        Strategy("AI", nn_df, Color(255, 128, 0, "orange")),
        Strategy("ETCC", heu_df, Color(0, 255, 183, "cyan")),
        saveroot="report",
    )
    comparator.compare(COMPARE_CONFS)


if __name__ == "__main__":
    main()
