import pathlib
from src.parsing import load_prebuilt_config


path2gamemaps_config = (
    "/Users/emax/Data/python/vsharp_searcher_bench/prebuilt/game_maps.json"
)
path2bizhawk_config = (
    "/Users/emax/Data/python/vsharp_searcher_bench/prebuilt/bizhawk.json"
)
path2jetbrains_lifetimes_config = (
    "/Users/emax/Data/python/vsharp_searcher_bench/prebuilt/jetbrains_lifetimes.json"
)
path2cosmos_os_config = (
    "/Users/emax/Data/python/vsharp_searcher_bench/prebuilt/cosmos_tasks.json"
)
path2powershell_config = (
    "/Users/emax/Data/python/vsharp_searcher_bench/prebuilt/powershell_tasks.json"
)
path2_unity_config = (
    "/Users/emax/Data/python/vsharp_searcher_bench/prebuilt/unity_tasks.json"
)

gamemaps = load_prebuilt_config(path2gamemaps_config)
bizhawk = load_prebuilt_config(path2bizhawk_config)
jetbrains_lifetimes = load_prebuilt_config(path2jetbrains_lifetimes_config)
cosmos_os = load_prebuilt_config(path2cosmos_os_config)
powershell = load_prebuilt_config(path2powershell_config)
unity = load_prebuilt_config(path2_unity_config)

all = gamemaps + bizhawk + jetbrains_lifetimes + unity


mapping = []

for item in powershell:
    mapping.append((pathlib.Path(item.dll).name, item.method))

import pandas as pd

df = pd.DataFrame(mapping, columns=["dll", "method"])

print(df)

df.to_csv("powershell.csv", index=False)
