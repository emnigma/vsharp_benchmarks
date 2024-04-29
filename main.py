import matplotlib.pyplot as plt
import pandas as pd


# searchstratcomp --(s)trategies --(p)arsedir


nn_res_path = "AI_all_new.csv"
heuristic_res_path = "ExecutionTreeContributedCoverage_all.csv"

nn_df = pd.read_csv(nn_res_path)
heu_df = pd.read_csv(heuristic_res_path)

set(pd.read_csv(nn_res_path)["method"]).symmetric_difference(
    set(pd.read_csv(heuristic_res_path)["method"])
)


def drop_failed(df: pd.DataFrame) -> int:
    failed = df[(df["coverage"] == -1)].index
    return failed


heu_df = heu_df.drop(drop_failed(heu_df))
nn_df = nn_df.drop(drop_failed(nn_df))

inner_df = heu_df.merge(nn_df, on="method", how="inner", suffixes=("ETCC", "AI"))

root = "report"

open(root + "/data.txt", "w").close()
with open(root + "/data.txt", "a") as file:
    file.write(",len(AI_more), len(VSharp_more), len(eq)\n")


def compare(
    dataframe: pd.DataFrame,
    on: str,
    desc: str,
    metric: str,
    divider_line: bool = False,
    less_is_winning: bool = False,
    logscale: bool = False,
    exp_name: str = None,
):
    AI_more = dataframe.loc[dataframe[f"{on}ETCC"] < dataframe[f"{on}AI"]]
    VSharp_more = dataframe.loc[dataframe[f"{on}ETCC"] > dataframe[f"{on}AI"]]
    eq = dataframe.loc[dataframe[f"{on}ETCC"] == dataframe[f"{on}AI"]]

    len(AI_more)
    len(VSharp_more)
    len(eq)
    print(exp_name)
    print(f"{len(AI_more)=}, {len(VSharp_more)=}, {len(eq)=}")

    if logscale:
        plt.xscale("log")
        plt.yscale("log")
        desc += ", logscale"

    if divider_line:
        plt.axline([0, 0], [1, 1])

    colors = ["green", "red", "black"]
    if less_is_winning:
        colors = ["red", "green", "black"]

    with open(root + "/data.txt", "a") as file:
        file.write(exp_name + ",")
        file.write(f"{len(AI_more)}, {len(VSharp_more)}, {len(eq)}\n")

    plt.scatter(AI_more[f"{on}ETCC"], AI_more[f"{on}AI"], color=colors[0])
    plt.scatter(VSharp_more[f"{on}ETCC"], VSharp_more[f"{on}AI"], color=colors[1])
    plt.scatter(eq[f"{on}ETCC"], eq[f"{on}AI"], color=colors[2])
    plt.xlabel(f"ETCC {on}, {metric}\n\n{on} comparison on the same methods\n{desc}")
    plt.ylabel(f"AI {on}, {metric}")
    savename = f"{on}.pdf" if exp_name is None else f"{exp_name}.pdf"
    plt.savefig(root + "/" + savename, format="pdf", bbox_inches="tight")
    # plt.show()


compare(
    dataframe=inner_df,
    on="coverage",
    desc="red: ETCC win, green: AI win, black: equal",
    metric="%",
    divider_line=True,
    exp_name="coverage",
)
compare(
    dataframe=inner_df,
    on="tests",
    desc="red: ETCC win, green: AI win, black: equal",
    metric="count",
    divider_line=True,
    less_is_winning=True,
    logscale=True,
    exp_name="tests",
)
compare(
    dataframe=inner_df,
    on="errors",
    desc="red: ETCC win, green: AI win, black: equal",
    metric="count",
    divider_line=True,
    logscale=True,
    exp_name="errors",
)
compare(
    dataframe=inner_df,
    on="total_time_sec",
    desc="red: ETCC win, green: AI win, black: equal",
    metric="s",
    divider_line=True,
    less_is_winning=True,
    exp_name="total_time_secs",
)

inner_coverage_eq = inner_df.loc[inner_df["coverageAI"] == inner_df["coverageETCC"]]

compare(
    dataframe=inner_coverage_eq,
    on="tests",
    desc="red: ETCC win, green: AI win, black: equal",
    metric="count",
    divider_line=True,
    less_is_winning=True,
    logscale=True,
    exp_name="tests_eq_coverage",
)
compare(
    dataframe=inner_coverage_eq,
    on="errors",
    desc="red: ETCC win, green: AI win, black: equal",
    metric="count",
    divider_line=True,
    logscale=True,
    exp_name="errors_eq_coverage",
)
compare(
    dataframe=inner_coverage_eq,
    on="total_time_sec",
    desc="red: ETCC win, green: AI win, black: equal",
    metric="s",
    divider_line=True,
    less_is_winning=True,
    logscale=True,
    exp_name="total_time_eq_coverage",
)
