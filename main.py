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
)
from src.structs import RunResult
from src.subprocess_calls import call_test_runner

"""
Prepare:
1) Remove double spaces in strs with methods
2) Remove multiline comments with methods
3) Build VSharp.Runner in Release mode: dotnet build -c Release
4) Build all required .dlls
5) Build VSharp.TestRunner
"""


def main():
    path2runer_wdir = "/Users/emax/Data/VSharp/VSharp.Runner/bin/Release/net7.0"
    path2runner = path2runer_wdir + "/VSharp.Runner.dll"
    output_test_folder = "/Users/emax/Data/python/vsharp_searcher_bench/gentests"
    strategy_name = "ExecutionTreeContributedCoverage"
    default_steps_limit = 30

    dll2methods = parse_maps("/Users/emax/Data/VSharp/VSharp.ML.GameServer/Maps.fs")
    gameserver_dataset = dll_prepend(
        dll_dir="/Users/emax/Data/VSharp/VSharp.ML.GameMaps/bin/Debug/net7.0/",
        dll2methods=dll2methods,
    )

    timestamp = str(datetime.fromtimestamp(datetime.now().timestamp()))
    log_file_name = f"bench{timestamp}.log"

    path2jetbrains_lifetimes_config = "/Users/emax/Data/python/vsharp_searcher_bench/prebuilt/jetbrains_lifetimes.json"
    path2cosmos_os_config = (
        "/Users/emax/Data/python/vsharp_searcher_bench/prebuilt/cosmos_tasks.json"
    )
    path2powershell_config = (
        "/Users/emax/Data/python/vsharp_searcher_bench/prebuilt/powershell_tasks.json"
    )
    path2_unity_config = (
        "/Users/emax/Data/python/vsharp_searcher_bench/prebuilt/unity_tasks.json"
    )

    jetbrains_lifetimes = load_prebuilt_config(
        path2jetbrains_lifetimes_config, default_steps_limit
    )
    cosmos_os = load_prebuilt_config(path2cosmos_os_config, default_steps_limit)
    powershell = load_prebuilt_config(path2powershell_config, default_steps_limit)
    unity = load_prebuilt_config(path2_unity_config, default_steps_limit)

    if os.path.exists(output_test_folder):
        shutil.rmtree(output_test_folder)
    os.makedirs(output_test_folder)

    launch_infos = (
        jetbrains_lifetimes + cosmos_os + powershell + unity + list(gameserver_dataset)
    )

    results = []

    for launch_info in tqdm.tqdm(list(launch_infos), desc=strategy_name):
        tests_path = f"{output_test_folder}/{launch_info.method}"
        runner_output = call_test_runner(
            path_to_runner=path2runner,
            launch_info=launch_info,
            default_steps_limit=default_steps_limit,
            strat_name=strategy_name,
            tests_path=tests_path,
            wdir=path2runer_wdir,
        )

        with open(log_file_name, "a+") as outfile:
            outfile.write(runner_output + "\n")

        (
            test_generated,
            errs_generated,
            steps_made,
            runner_coverage,
        ) = parse_runner_output(runner_output)

        results.append(
            attrs.asdict(
                RunResult(
                    method=launch_info.method,
                    steps_made=steps_made,
                    tests=test_generated,
                    errors=errs_generated,
                    precise_coverage_percent=runner_coverage,
                )
            )
        )

        with open(log_file_name, "a+") as outfile:
            outfile.write("_" * 20 + "\n")

        df = pd.DataFrame(results)
        df.to_csv(f"{strategy_name}.csv", index=False)


if __name__ == "__main__":
    main()
