import os
import warnings

import attrs
import matplotlib.pyplot as plt
import pandas as pd

# searchstratcomp --(s)trategies --(p)arsedir


@attrs.define
class Color:
    r: int
    g: int
    b: int

    name: str

    def to_rgb(self):
        return (self.r / 255, self.g / 255, self.b / 255)


@attrs.define
class Strategy:
    strategy_name: str
    strategy_df: pd.DataFrame


class Comparator:
    def __init__(self, strat1: Strategy, strat2: Strategy, saveroot: str) -> None:
        os.makedirs(saveroot, exist_ok=True)
        self.saveroot = saveroot
        self.strat1 = strat1
        self.strat2 = strat2
        self.result_count_df = pd.DataFrame(
            columns=[f"{strat1.strategy_name}_won", f"{strat2.strategy_name}_won", "eq"]
        )

        self.drop_failed()

    def _drop_failed(self, df: pd.DataFrame) -> pd.DataFrame:
        failed = df[(df["coverage"] == -1)].index
        return df.drop(failed)

    def drop_failed(self) -> int:
        self.strat1.strategy_df = self._drop_failed(self.strat1.strategy_df)
        self.strat2.strategy_df = self._drop_failed(self.strat2.strategy_df)

    def _compare(
        self,
        dataframe: pd.DataFrame,
        on: str,
        metric: str,
        divider_line: bool = False,
        less_is_winning: bool = False,
        logscale: bool = False,
        exp_name: str = None,
    ):
        strat1_color = Color(255, 128, 0, "orange")
        strat2_color = Color(0, 255, 183, "cyan")

        def left_win_comparison(left, right):
            if less_is_winning:
                return left < right
            return left > right

        strat1_win = dataframe.loc[
            left_win_comparison(dataframe[f"{on}{strat2}"], dataframe[f"{on}{strat1}"])
        ]
        strat2_win = dataframe.loc[
            left_win_comparison(dataframe[f"{on}{strat1}"], dataframe[f"{on}{strat2}"])
        ]
        eq = dataframe.loc[dataframe[f"{on}{strat2}"] == dataframe[f"{on}{strat1}"]]

        print(f"{len(strat1_win)=}, {len(strat2_win)=}, {len(eq)=}")

        scale = "linscale"
        if logscale:
            plt.xscale("log")
            plt.yscale("log")
            scale = "logscale"

        if divider_line:
            plt.axline([0, 0], [1, 1])

        # check if exp_name already exists in df:
        if exp_name in self.result_count_df.index:
            warnings.warn(f"Overwriting {exp_name} in result_count_df")

        self.result_count_df.loc[exp_name] = [len(strat1_win), len(strat2_win), len(eq)]

        plt.scatter(
            strat1_win[f"{on}{strat2}"],
            strat1_win[f"{on}{strat1}"],
            color=[strat1_color.to_rgb()],
        )
        plt.scatter(
            strat2_win[f"{on}{strat2}"],
            strat2_win[f"{on}{strat1}"],
            color=[strat2_color.to_rgb()],
        )
        plt.scatter(eq[f"{on}{strat2}"], eq[f"{on}{strat1}"], color="black")
        plt.xlabel(
            f"{strat2} {on}, {metric}\n\n{on} comparison on the same methods, {scale}\n"
            f"{strat1} ({strat1_color.name}) won: {len(strat1_win)}, "
            f"{strat2} ({strat2_color.name}) won: {len(strat2_win)}, eq: {len(eq)}"
        )
        plt.ylabel(f"{strat1} {on}, {metric}")
        savename = f"{on}.pdf" if exp_name is None else f"{exp_name}.pdf"
        plt.savefig(
            os.path.join(self.saveroot, savename), format="pdf", bbox_inches="tight"
        )

    def compare(self):
        self.inner_df = self.strat1.strategy_df.merge(
            self.strat2.strategy_df,
            on="method",
            how="inner",
            suffixes=(self.strat1.strategy_name, self.strat2.strategy_name),
        )
        self._compare(
            dataframe=self.inner_df,
            on="coverage",
            metric="%",
            divider_line=True,
            exp_name="coverage",
        )
        self._compare(
            dataframe=self.inner_df,
            on="tests",
            metric="count",
            divider_line=True,
            less_is_winning=True,
            logscale=True,
            exp_name="tests",
        )
        self._compare(
            dataframe=self.inner_df,
            on="errors",
            metric="count",
            divider_line=True,
            logscale=True,
            exp_name="errors",
        )
        self._compare(
            dataframe=self.inner_df,
            on="total_time_sec",
            metric="s",
            divider_line=True,
            less_is_winning=True,
            exp_name="total_time_secs",
        )

        inner_coverage_eq = self.inner_df.loc[
            self.inner_df[f"coverage{strat1}"] == self.inner_df[f"coverage{strat2}"]
        ]

        self._compare(
            dataframe=inner_coverage_eq,
            on="tests",
            metric="count",
            divider_line=True,
            less_is_winning=True,
            logscale=True,
            exp_name="tests_eq_coverage",
        )
        self._compare(
            dataframe=inner_coverage_eq,
            on="errors",
            metric="count",
            divider_line=True,
            logscale=True,
            exp_name="errors_eq_coverage",
        )
        self._compare(
            dataframe=inner_coverage_eq,
            on="total_time_sec",
            metric="s",
            divider_line=True,
            less_is_winning=True,
            logscale=True,
            exp_name="total_time_eq_coverage",
        )

        self.result_count_df.to_csv(os.path.join(self.saveroot, "result_count.csv"))


nn_res_path = "AI_all_new.csv"
heuristic_res_path = "ExecutionTreeContributedCoverage_all.csv"

strat1 = "AI"
strat2 = "ETCC"


nn_df = pd.read_csv(nn_res_path)
heu_df = pd.read_csv(heuristic_res_path)


comparator = Comparator(
    Strategy("AI", nn_df), Strategy("ETCC", heu_df), saveroot="report"
)
comparator.compare()

# set(pd.read_csv(nn_res_path)["method"]).symmetric_difference(
#     set(pd.read_csv(heuristic_res_path)["method"])
# )


# def drop_failed(df: pd.DataFrame) -> int:
#     failed = df[(df["coverage"] == -1)].index
#     return failed
