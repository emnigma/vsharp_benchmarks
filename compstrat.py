import argparse

import attrs
import pandas as pd

from compare_configs import COMPARE_CONFS
from src.comparator import Color, Comparator, Strategy


@attrs.define
class Args:
    strat1: str
    run1: str
    strat2: str
    run2: str


def entrypoint(args: Args):
    def create(strat, run, color):
        return Strategy(strat, pd.read_csv(run), color)

    philippine_orange = Color(255, 115, 0, "orange")
    blue_sparkle = Color(0, 119, 255, "blue")
    comparator = Comparator(
        create(args.strat1, args.run1, philippine_orange),
        create(args.strat2, args.run2, blue_sparkle),
        saveroot="report",
    )
    comparator.compare(COMPARE_CONFS)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s1",
        "--strat1",
        type=str,
        required=True,
        help="Name of the first strategy",
    )
    parser.add_argument(
        "-r1",
        "--run1",
        type=str,
        required=True,
        help="Path to the first strategy run result",
    )
    parser.add_argument(
        "-s2",
        "--strat2",
        type=str,
        required=True,
        help="Name of the second strategy",
    )
    parser.add_argument(
        "-r2",
        "--run2",
        type=str,
        required=True,
        help="Path to ther second strategy run result",
    )
    args = parser.parse_args()

    entrypoint(Args(**vars(args)))


if __name__ == "__main__":
    main()
