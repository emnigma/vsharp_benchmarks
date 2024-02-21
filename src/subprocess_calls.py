import subprocess

import func_timeout

from src.structs import LaunchInfo


def call_test_runner(
    path_to_runner: str,
    launch_info: LaunchInfo,
    strat_name: str,
    wdir: str,
    timeout: int,
    model_path: str,
):
    call = [
        "dotnet",
        path_to_runner,
        "--method",
        launch_info.method,
        launch_info.dll,
        "--timeout",
        str(timeout),
        "--strat",
        strat_name,
        "--check-coverage",
        "--model",
        model_path,
    ]

    def runner_fun(call, wdir):
        return subprocess.check_output(call, stderr=subprocess.STDOUT, cwd=wdir).decode(
            "utf-8"
        )

    try:
        runner_output = func_timeout.func_timeout(
            timeout=timeout + 1, func=runner_fun, kwargs={"call": call, "wdir": wdir}
        )

    except subprocess.CalledProcessError:
        raise
    except func_timeout.FunctionTimedOut:
        raise

    return " ".join(map(str, call)), runner_output
