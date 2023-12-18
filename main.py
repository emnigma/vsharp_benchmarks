import json
import os
import shutil
from datetime import datetime

import attrs
import pandas as pd
import tqdm

from src.parsing import (
    dll_prepend,
    load_prebuilt_config,
    parse_maps,
    parse_runner_output,
    recurse_find,
)
from src.structs import RunResult
from src.subprocess_calls import call_dotcover, call_test_runner

"""
Prepare:
1) Remove double spaces in strs with methods
2) Remove multiline comments with methods
3) Build VSharp.Runner in Release mode: dotnet build -c Release .
4) Build all required .dlls
5) Build VSharp.TestRunner
"""


def main():
    path2runner = (
        "/Users/emax/Data/VSharp/VSharp.Runner/bin/Release/net7.0/VSharp.Runner"
    )
    path2test_runner_dll = "/Users/emax/Data/VSharp/VSharp.TestRunner/bin/Release/net7.0/VSharp.TestRunner.dll"
    output_test_folder = "./gentests"
    strategy_name = "ExecutionTreeContributedCoverage"
    default_steps_limit = 3000

    dll2methods = parse_maps("/Users/emax/Data/VSharp/VSharp.ML.GameServer/Maps.fs")
    gameserver_dataset = dll_prepend(
        dll_dir="/Users/emax/Data/VSharp/VSharp.ML.GameMaps/bin/Debug/net7.0/",
        dll2methods=dll2methods,
    )

    timestamp = str(datetime.fromtimestamp(datetime.now().timestamp()))
    log_file_name = f"bench{timestamp}.log"

    path2cosmos_os_config = (
        "/Users/emax/Data/python/vsharp_searcher_bench/prebuilt/cosmos_tasks.json"
    )
    path2powershell_config = (
        "/Users/emax/Data/python/vsharp_searcher_bench/prebuilt/powershell_tasks.json"
    )
    path2_unity_config = (
        "/Users/emax/Data/python/vsharp_searcher_bench/prebuilt/unity_tasks.json"
    )

    # cosmos_os = load_prebuilt_config(path2cosmos_os_config, default_steps_limit)
    powershell = load_prebuilt_config(path2powershell_config, default_steps_limit)
    unity = load_prebuilt_config(path2_unity_config, default_steps_limit)

    if os.path.exists(output_test_folder):
        shutil.rmtree(output_test_folder)
    os.makedirs(output_test_folder)

    launch_infos = powershell + unity + list(gameserver_dataset)

    results = []

    for launch_info in tqdm.tqdm(list(launch_infos), desc=strategy_name):
        tests_path = f"{output_test_folder}/{launch_info.method}"
        runner_output = call_test_runner(
            path_to_runner=path2runner,
            launch_info=launch_info,
            default_steps_limit=default_steps_limit,
            strat_name=strategy_name,
            tests_path=tests_path,
        )

        with open(log_file_name, "a+") as outfile:
            outfile.write(runner_output + "\n")

        (
            test_generated,
            errs_generated,
            steps_made,
            runner_coverage,
        ) = parse_runner_output(runner_output)

        call_dotcover(
            path2test_runner_dll=path2test_runner_dll,
            tests_path=tests_path,
            log_path=log_file_name,
        )
        with open(
            "dotCover.Output.json", "r", encoding="utf-8-sig"
        ) as dotcover_out_file:
            dotcover_out = json.load(dotcover_out_file)

        if (
            dotcover_coverage := recurse_find(
                launch_info.method.split("."), dotcover_out
            )
            != None
        ):
            dotcover_coverage = dotcover_coverage["CoveragePercent"]
        else:
            dotcover_coverage = 0

        results.append(
            attrs.asdict(
                RunResult(
                    method=launch_info.method,
                    steps_made=steps_made,
                    tests=test_generated,
                    errors=errs_generated,
                    runner_coverage_percent=runner_coverage,
                    dotcover_coverage_percent=dotcover_coverage,
                )
            )
        )

        df = pd.DataFrame(results)
        df.to_csv(f"{strategy_name}.csv", index=False)


if __name__ == "__main__":
    main()
