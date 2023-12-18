import subprocess

from src.structs import LaunchInfo


def call_test_runner(
    path_to_runner: str,
    launch_info: LaunchInfo,
    default_steps_limit: int,
    strat_name: str,
    tests_path: str,
):
    call = [
        path_to_runner,
        "--method",
        launch_info.method,
        launch_info.dll,
        "--timeout",
        str(-1),
        "--steps-limit",
        str(launch_info.steps) if launch_info.steps else str(default_steps_limit),
        "--strat",
        strat_name,
        "--output",
        tests_path,
    ]

    runner_output = subprocess.check_output(call, stderr=subprocess.STDOUT).decode(
        "utf-8"
    )
    if "Error:" in runner_output:
        raise RuntimeError(f"call {' '.join(call)}\n failed with {runner_output}")

    return runner_output


def call_vsharp_coverage_tool():
    "/Users/emax/Data/VSharp/VSharp.TestRunner/bin/Release/net7.0/VSharp.TestRunner"

def call_dotcover(path2test_runner_dll: str, tests_path: str, log_path: str):
    dotcover_call = [
        "dotnet",
        "dotcover",
        '--dcFilters="-:module=FSharp.*;-:class=VSharp.*;-:module=VSharp.Utils"',
        path2test_runner_dll,
        tests_path + "/VSharp.tests.0",
        "--dcReportType=JSON",
        "--dcDisableDefaultFilters",
    ]
    with open(log_path, "a+") as outfile:
        subprocess.run(
            " ".join(dotcover_call),
            shell=True,
            stdout=outfile,
            stderr=subprocess.STDOUT,
        )
