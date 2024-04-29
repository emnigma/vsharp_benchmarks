import argparse
import pathlib

from comparator import Strategy, Comparator
from compare_configs import COMPARE_CONFS
from runstrat import entrypoint as runstrat_entrypoint, Args, AssemblyInfo


class SearchStrategyComparison:
    def __init__(self, strategy_names: list[str]) -> None:
        pass

    def run(
        strat: str, pysymgym_path: pathlib.Path, assembly_infos: list[AssemblyInfo]
    ):
        return runstrat_entrypoint(
            Args(
                strategy=strat,
                timeout=60,
                pysymgym_path=pysymgym_path,
                assembly_infos=assembly_infos,
            )
        )

    def compare(strat1: Strategy, strat2: Strategy, saveroot: str):
        comparator = Comparator(strat1, strat2, saveroot)
        comparator.compare(COMPARE_CONFS)


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
        "rootdir",
        dest="rootdir",
        type=pathlib.Path,
        required=False,
        help="Directory containing runs results",
    )

    args = parser.parse_args()


if __name__ == "__main__":
    main()
