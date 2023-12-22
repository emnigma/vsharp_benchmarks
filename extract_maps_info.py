import argparse
import json
from collections import defaultdict

from src.parsing import dll_prepend, parse_maps


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("maps_file", type=str, help="path to Maps.fs")
    parser.add_argument("dll_dir", type=str, help="path to dir, containing maps dlls")
    parser.add_argument(
        "--savepath",
        type=str,
        help="path to save result to",
        default="./game_maps.json",
    )

    args = parser.parse_args()

    dll2methods = parse_maps(args.maps_file)
    gameserver_dataset = dll_prepend(
        dll_dir="/Users/emax/Data/VSharp/VSharp.ML.GameMaps/bin/Debug/net7.0/",
        dll2methods=dll2methods,
    )

    rst = defaultdict(lambda: defaultdict(list))

    for l_info in gameserver_dataset:
        full_qual = l_info.method.split(".")
        clazz, method = ".".join(full_qual[:-1]), full_qual[-1]
        method_l_info = method if l_info.steps is None else (method, int(l_info.steps))
        rst[l_info.dll][clazz].append(method_l_info)

    rst = {"dll_dir": args.dll_dir, "dlls": rst}

    with open(args.savepath, "w") as savefile:
        json.dump(rst, savefile)


if __name__ == "__main__":
    main()
