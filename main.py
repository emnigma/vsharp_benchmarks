import argparse
import itertools
import logging
import pathlib
import subprocess
from datetime import datetime

import attrs
import func_timeout
import pandas as pd
import tqdm

from src.parsing import load_config, parse_runner_output
from src.structs import RunResult
from src.subprocess_calls import call_test_runner

timestamp = datetime.fromtimestamp(datetime.now().timestamp())


PYSYMGYM_ROOT = pathlib.Path("...")


def setup_logging(strategy):
    logging.basicConfig(
        filename=f"{strategy}_{timestamp}.log",
        format="%(asctime)s - p%(process)d: %(name)s - [%(levelname)s]: %(message)s",
        level=logging.INFO,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--strategy", type=str, required=True, help="V# searcher strategy"
    )
    parser.add_argument(
        "-t", "--timeout", type=int, required=True, help="V# runner timeout"
    )
    parser.add_argument(
        "--root-project-path",
        type=pathlib.Path,
        dest="root_project_path",
        default=pathlib.Path(
            PYSYMGYM_ROOT / "maps/DotNet/Maps/Root/bin/Release/net7.0"
        ).absolute(),
        help="Absolute path to VSharp",
    )
    parser.add_argument(
        "--runner-path",
        type=pathlib.Path,
        dest="runner_path",
        default=pathlib.Path(
            PYSYMGYM_ROOT
            / "GameServers/VSharp/VSharp.Runner/bin/Release/net7.0/VSharp.Runner.dll"
        ).absolute(),
        help="Absolute path to VSharp.Runner.dll",
    )
    parser.add_argument(
        "--model-path",
        type=pathlib.Path,
        dest="model_path",
        default=pathlib.Path(
            PYSYMGYM_ROOT / "GameServers/VSharp/VSharp.Explorer/models/model.onnx"
        ).absolute(),
        help="Absolute path to model.onnx",
    )
    parser.add_argument(
        "-as",
        "--assembly-infos",
        type=pathlib.Path,
        dest="assembly_infos",
        action="append",
        nargs=2,
        metavar=("dlls-path", "launch-info-path"),
        help="Provide tuples: dir with dlls/assembly info file",
    )

    args = parser.parse_args()

    setup_logging(strategy=args.strategy)

    assembled = list(
        itertools.chain(
            *[
                load_config(dll_path, launch_info)
                for dll_path, launch_info in args.assembly_infos
            ]
        )
    )

    logging.info(args)
    results = []

    for launch_info in tqdm.tqdm(assembled, desc=args.strategy):
        try:
            call, runner_output = call_test_runner(
                path_to_runner=args.runner_path,
                launch_info=launch_info,
                strat_name=args.strategy,
                wdir=args.runner_path.parent,
                timeout=args.timeout,
                model_path=args.model_path,
            )
        except subprocess.CalledProcessError as cpe:
            logging.error(
                f"""
                runner threw {cpe} on {launch_info.method}, this method will be skipped
                runner output: {cpe.output}
                cmd: {cpe.cmd}
                """
            )
            continue
        except func_timeout.FunctionTimedOut as fto:
            logging.error(
                f"""
                runner timed out on {launch_info.method}, this method will be skipped
                cmd: {" ".join(map(str,fto.timedOutKwargs["call"]))}
                """
            )
            continue

        try:
            (
                total_time,
                test_generated,
                errs_generated,
                runner_coverage,
            ) = parse_runner_output(runner_output)
        except AttributeError as e:
            logging.error(
                f"""
                {e} thrown on {launch_info.method}, this method will be skipped
                runner output: {runner_output}
                cmd: {call}
                """
            )
            continue

        run_result = RunResult(
            method=launch_info.method,
            tests=test_generated,
            errors=errs_generated,
            coverage=runner_coverage,
            total_time_sec=total_time,
        )

        logging.info(f"method {launch_info.method} completed with {run_result}")

        results.append(attrs.asdict(run_result))

        df = pd.DataFrame(results)
        df.to_csv(f"{args.strategy}_{timestamp}.csv", index=False)


if __name__ == "__main__":
    main()
