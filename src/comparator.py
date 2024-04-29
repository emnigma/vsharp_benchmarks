import enum
import json
import os
import warnings

import attrs
import matplotlib.pyplot as plt
import pandas as pd


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
    color: Color


class DataSourceType(enum.Enum):
    RAW_DF = "Unprocessed dataframe"
    INNER_JOIN_DF = "Inner join dataframe"
    INNER_JOIN_COVERAGE_EQ_DF = "Inner join dataframe with equal coverage"


@attrs.define
class CompareConfig:
    datasource: DataSourceType
    by_column: str
    metric: str
    divider_line: bool = False
    less_is_winning: bool = False
    logscale: bool = False
    exp_name: str = None


class Comparator:
    def __init__(self, strat1: Strategy, strat2: Strategy, saveroot: str) -> None:
        os.makedirs(saveroot, exist_ok=True)
        self.saveroot = saveroot
        self.strat1 = strat1
        self.strat2 = strat2
        self.result_count_df = pd.DataFrame(
            columns=[f"{strat1.strategy_name}_won", f"{strat2.strategy_name}_won", "eq"]
        )

        with open(os.path.join(self.saveroot, "symdiff_starts_methods.json"), "w") as f:
            json.dump(
                list(
                    set(strat1.strategy_df["method"]).symmetric_difference(
                        set(strat2.strategy_df["method"])
                    )
                ),
                f,
                indent=4,
            )
        self.drop_failed()

        self.inner_df = self.strat1.strategy_df.merge(
            self.strat2.strategy_df,
            on="method",
            how="inner",
            suffixes=(self.strat1.strategy_name, self.strat2.strategy_name),
        )

        self.inner_coverage_eq = self.inner_df.loc[
            self.inner_df[f"coverage{self.strat1.strategy_name}"]
            == self.inner_df[f"coverage{self.strat2.strategy_name}"]
        ]

    def _drop_failed(self, df: pd.DataFrame) -> pd.DataFrame:
        failed = df[(df["coverage"] == -1)].index
        return df.drop(failed)

    def drop_failed(self) -> int:
        self.strat1.strategy_df = self._drop_failed(self.strat1.strategy_df)
        self.strat2.strategy_df = self._drop_failed(self.strat2.strategy_df)

    def _compare(self, config: CompareConfig):
        def left_win_comparison(left, right):
            if config.less_is_winning:
                return left < right
            return left > right

        match config.datasource:
            case DataSourceType.RAW_DF:
                dataframe = self.inner_df
            case DataSourceType.INNER_JOIN_DF:
                dataframe = self.inner_df
            case DataSourceType.INNER_JOIN_COVERAGE_EQ_DF:
                dataframe = self.inner_coverage_eq

        strat1_win = dataframe.loc[
            left_win_comparison(
                dataframe[f"{config.by_column}{self.strat2.strategy_name}"],
                dataframe[f"{config.by_column}{self.strat1.strategy_name}"],
            )
        ]
        strat2_win = dataframe.loc[
            left_win_comparison(
                dataframe[f"{config.by_column}{self.strat1.strategy_name}"],
                dataframe[f"{config.by_column}{self.strat2.strategy_name}"],
            )
        ]
        eq = dataframe.loc[
            dataframe[f"{config.by_column}{self.strat2.strategy_name}"]
            == dataframe[f"{config.by_column}{self.strat1.strategy_name}"]
        ]

        print(f"{len(strat1_win)=}, {len(strat2_win)=}, {len(eq)=}")

        scale = "linscale"
        if config.logscale:
            plt.xscale("log")
            plt.yscale("log")
            scale = "logscale"

        if config.divider_line:
            plt.axline([0, 0], [1, 1])

        # check if exp_name already exists in df:
        if config.exp_name in self.result_count_df.index:
            warnings.warn(f"Overwriting {config.exp_name} in result_count_df")

        self.result_count_df.loc[config.exp_name] = [
            len(strat1_win),
            len(strat2_win),
            len(eq),
        ]

        plt.scatter(
            strat1_win[f"{config.by_column}{self.strat2.strategy_name}"],
            strat1_win[f"{config.by_column}{self.strat1.strategy_name}"],
            color=[self.strat1.color.to_rgb()],
        )

        plt.scatter(
            strat2_win[f"{config.by_column}{self.strat2.strategy_name}"],
            strat2_win[f"{config.by_column}{self.strat1.strategy_name}"],
            color=[self.strat2.color.to_rgb()],
        )
        plt.scatter(
            eq[f"{config.by_column}{self.strat2.strategy_name}"],
            eq[f"{config.by_column}{self.strat1.strategy_name}"],
            color="black",
        )
        plt.xlabel(
            f"{self.strat2.strategy_name} {config.by_column}, {config.metric}\n\n{config.by_column} comparison on the same methods, {scale}\n"
            f"{self.strat1.strategy_name} ({self.strat1.color.name}) won: {len(strat1_win)}, "
            f"{self.strat2.strategy_name} ({self.strat2.color.name}) won: {len(strat2_win)}, eq: {len(eq)}"
        )
        plt.ylabel(f"{self.strat1.strategy_name} {config.by_column}, {config.metric}")
        savename = (
            f"{config.on}.pdf" if config.exp_name is None else f"{config.exp_name}.pdf"
        )
        plt.savefig(
            os.path.join(self.saveroot, savename), format="pdf", bbox_inches="tight"
        )

    def compare(self, configs: list[CompareConfig]):
        for config in configs:
            self._compare(config)

        self.result_count_df.to_csv(os.path.join(self.saveroot, "result_count.csv"))
