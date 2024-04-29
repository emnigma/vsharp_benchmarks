from collections import defaultdict

import matplotlib.pyplot as plt
import pandas as pd
import attrs
# searchstratcomp --(s)trategies --(p)arsedir


nn_res_path = "AI_all_new.csv"
heuristic_res_path = "ExecutionTreeContributedCoverage_all.csv"

strat1 = "AI"
strat2 = "ETCC"


@attrs.define
class Strategy:
    strategy_name: str
    strategy_df: pd.DataFrame


class Comparator:
    def __init__(self, strat1: Strategy, strat2: Strategy) -> None:
        self.strat1 = strat1
        self.strat2 = strat2

    def _drop_failed(self, df: pd.DataFrame) -> pd.DataFrame:
        failed = df[(df["coverage"] == -1)].index
        return df.drop(failed)

    def drop_failed(self) -> int:
        self.strat1.strategy_df.replace(self._drop_failed(self.strat1.strategy_df))
        self.strat2.strategy_df.replace(self._drop_failed(self.strat2.strategy_df))

    def compare(self):
        pass


nn_df = pd.read_csv(nn_res_path)
heu_df = pd.read_csv(heuristic_res_path)

set(pd.read_csv(nn_res_path)["method"]).symmetric_difference(
    set(pd.read_csv(heuristic_res_path)["method"])
)


def drop_failed(df: pd.DataFrame) -> int:
    failed = df[(df["coverage"] == -1)].index
    return failed


heu_df = heu_df.drop(drop_failed(heu_df))
nn_df = nn_df.drop(drop_failed(nn_df))

inner_df = heu_df.merge(nn_df, on="method", how="inner", suffixes=(strat2, strat1))

root = "report"

open(root + "/data.txt", "w").close()
with open(root + "/data.txt", "a") as file:
    file.write(f",len({strat1}_more), len({strat2}_more), len(eq)\n")

result_count_df = pd.DataFrame(columns=[f"{strat1}_won", f"{strat2}_won", "eq"])


def compare(
    dataframe: pd.DataFrame,
    on: str,
    desc: str,
    metric: str,
    divider_line: bool = False,
    less_is_winning: bool = False,
    logscale: bool = False,
    exp_name: str = None,
):
    
    strat1_more = dataframe.loc[dataframe[f"{on}{strat2}"] < dataframe[f"{on}{strat1}"]]
    strat2_more = dataframe.loc[dataframe[f"{on}{strat1}"] > dataframe[f"{on}{strat1}"]]
    eq = dataframe.loc[dataframe[f"{on}{strat1}"] == dataframe[f"{on}{strat1}"]]

    print(f"{len(strat1_more)=}, {len(strat2_more)=}, {len(eq)=}")

    if logscale:
        plt.xscale("log")
        plt.yscale("log")
        desc += ", logscale"

    if divider_line:
        plt.axline([0, 0], [1, 1])

    colors = ["green", "red", "black"]
    if less_is_winning:
        colors = ["red", "green", "black"]

    with open(root + "/data.txt", "a") as file:
        file.write(exp_name + ",")
        file.write(f"{len(strat1_more)}, {len(strat2_more)}, {len(eq)}\n")

    # result_count_df.loc[exp_name] = [len(strat1_more), len(strat2_more), len(eq)]

    plt.scatter(
        strat1_more[f"{on}{strat2}"], strat1_more[f"{on}{strat1}"], color=colors[0]
    )
    plt.scatter(
        strat2_more[f"{on}{strat2}"], strat2_more[f"{on}{strat1}"], color=colors[1]
    )
    plt.scatter(eq[f"{on}{strat2}"], eq[f"{on}{strat1}"], color=colors[2])
    plt.xlabel(
        f"{strat2} {on}, {metric}\n\n{on} comparison on the same methods\n{desc}"
    )
    plt.ylabel(f"{strat1} {on}, {metric}")
    savename = f"{on}.pdf" if exp_name is None else f"{exp_name}.pdf"
    plt.savefig(root + "/" + savename, format="pdf", bbox_inches="tight")
    # plt.show()


compare(
    dataframe=inner_df,
    on="coverage",
    desc=f"red: {strat2} win, green: {strat1} win, black: equal",
    metric="%",
    divider_line=True,
    exp_name="coverage",
)
compare(
    dataframe=inner_df,
    on="tests",
    desc=f"red: {strat2} win, green: {strat1} win, black: equal",
    metric="count",
    divider_line=True,
    less_is_winning=True,
    logscale=True,
    exp_name="tests",
)
compare(
    dataframe=inner_df,
    on="errors",
    desc=f"red: {strat2} win, green: {strat1} win, black: equal",
    metric="count",
    divider_line=True,
    logscale=True,
    exp_name="errors",
)
compare(
    dataframe=inner_df,
    on="total_time_sec",
    desc=f"red: {strat2} win, green: {strat1} win, black: equal",
    metric="s",
    divider_line=True,
    less_is_winning=True,
    exp_name="total_time_secs",
)

inner_coverage_eq = inner_df.loc[
    inner_df[f"coverage{strat1}"] == inner_df[f"coverage{strat2}"]
]

compare(
    dataframe=inner_coverage_eq,
    on="tests",
    desc=f"red: {strat2} win, green: {strat1} win, black: equal",
    metric="count",
    divider_line=True,
    less_is_winning=True,
    logscale=True,
    exp_name="tests_eq_coverage",
)
compare(
    dataframe=inner_coverage_eq,
    on="errors",
    desc=f"red: {strat2} win, green: {strat1} win, black: equal",
    metric="count",
    divider_line=True,
    logscale=True,
    exp_name="errors_eq_coverage",
)
compare(
    dataframe=inner_coverage_eq,
    on="total_time_sec",
    desc=f"red: {strat2} win, green: {strat1} win, black: equal",
    metric="s",
    divider_line=True,
    less_is_winning=True,
    logscale=True,
    exp_name="total_time_eq_coverage",
)
