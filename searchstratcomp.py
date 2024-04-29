import argparse
import pathlib

# searchstratcomp --(s)trategies --(p)arsedir


def run(strat: str, parsedir: pathlib.Path):
    pass

def compare(strat1: str, strat2: str, parsedir: pathlib.Path):
    pass

def main():
    parser = argparse.ArgumentParser(description="Search Strategy Comparison")

    parser.add_argument(
        "s",
        "strategies",
        dest="strategies",
        type=pathlib.Path,
        nargs="*",
        required=False,
        help="Strategies to compare",
    )
    parser.add_argument(
        "p",
        "parsedir",
        dest="parsedir",
        type=pathlib.Path,
        required=False,
        help="Directory containing the parsed results",
    )

    args = parser.parse_args()


if __name__ == "__main__":
    main()
