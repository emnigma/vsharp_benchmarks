import argparse

import pandas as pd


def remove_generic_indicators(df: pd.DataFrame):
    df["method"] = df["method"].map(lambda method: method.replace("`1", ""))
    return df


def prepare_nn_res(nn_res_df: pd.DataFrame) -> pd.DataFrame:
    return nn_res_df.rename(
        lambda x: f"{x}__nn" if x != "method" else "method", axis="columns"
    )


def prepare_heu_res(heu_res: pd.DataFrame) -> pd.DataFrame:
    return remove_generic_indicators(heu_res)


def main():
    parser = argparse.ArgumentParser(
        description="This program joins evaluations for NN and V# heuristic"
    )
    parser.add_argument(
        "-nn",
        dest="nn_res_path",
        type=str,
        required=True,
        help="path to nn results .csv",
    )
    parser.add_argument(
        "-he",
        dest="heuristic_res_path",
        type=str,
        required=True,
        help="path to heuristic results .csv",
    )
    parser.add_argument(
        "--savepath",
        type=str,
        help="path to save result to",
        default="joined.csv",
    )

    parser.add_argument(
        "--method",
        type=str,
        help="type of merge to be performed",
        choices=["left", "right", "outer", "inner", "cross"],
        default="inner",
    )
    args = parser.parse_args()

    nn_res_df = pd.read_csv(args.nn_res_path)
    heuristic_res_df = pd.read_csv(args.heuristic_res_path)

    nn_res_df = prepare_nn_res(nn_res_df)
    heuristic_res_df = prepare_heu_res(heuristic_res_df)

    joined = heuristic_res_df.merge(nn_res_df, on="method", how=args.method)

    joined.to_csv(args.savepath)


if __name__ == "__main__":
    main()
