import pandas as pd
import argparse

from compare_configs import COMPARE_CONFS
from src.comparator import Color, Comparator, Strategy


def entrypoint(args):
    df1 = pd.read_csv(args.run1)
    df2 = pd.read_csv(args.run2)

    comparator = Comparator(
        Strategy(args.strat1, df1, Color(255, 128, 0, "orange")),
        Strategy(args.strat2, df2, Color(0, 255, 183, "cyan")),
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

    print(args)
    entrypoint(args)


if __name__ == "__main__":
    main()
