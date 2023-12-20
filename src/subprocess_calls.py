import subprocess

from src.structs import LaunchInfo


def call_test_runner(
    path_to_runner: str,
    launch_info: LaunchInfo,
    default_steps_limit: int,
    strat_name: str,
    tests_path: str,
    wdir: str,
):
    call = [
        "dotnet",
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
        "--check-coverage",
    ]

    print(" ".join(call))

    runner_output = subprocess.check_output(
        call, stderr=subprocess.STDOUT, cwd=wdir
    ).decode("utf-8")
    if "Error:" in runner_output:
        raise RuntimeError(f"call {' '.join(call)}\n failed with {runner_output}")

    return runner_output
