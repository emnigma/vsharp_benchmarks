# Howto:

## Installation

```bash
python3 -m venv .env
soure .env/bin/activate
pip install -r requirements.txt
```

## Usage

Docs:

```bash
usage: main.py [-h] -s STRATEGY -t TIMEOUT [-ps PYSYMGYM_PATH] [-as dlls-path launch-info-path]

options:
  -h, --help            show this help message and exit
  -s STRATEGY, --strategy STRATEGY
                        V# searcher strategy
  -t TIMEOUT, --timeout TIMEOUT
                        V# runner timeout
  -ps PYSYMGYM_PATH, --pysymgym-path PYSYMGYM_PATH
                        Absolute path to PySymGym
  -as dlls-path launch-info-path, --assembly-infos dlls-path launch-info-path
                        Provide tuples: dir with dlls/assembly info file
```

To start benchmark, run

```bash
python3 main.py \
    --strategy AI \
    --timeout 120 \
    --pysymgym-path /Users/emax/Data/PySymGym \
    --assembly-infos /Users/emax/Data/PySymGym/maps/DotNet/Maps/Root/bin/Release/net7.0 /Users/emax/Data/python/vsharp_searcher_bench/prebuilt/assembled.csv \
    --assembly-infos /Users/emax/Data/python/vsharp_searcher_bench/prebuilt/cosmos/publish prebuilt/cosmos_os.csv \
    --assembly-infos /Users/emax/Data/python/vsharp_searcher_bench/prebuilt/powershell-osx-arm64 prebuilt/powershell.csv
```

Or shortened version:

```bash
python3 main.py \
    -s AI \
    -t 120 \
    -ps /Users/emax/Data/PySymGym \
    -as /Users/emax/Data/PySymGym/maps/DotNet/Maps/Root/bin/Release/net7.0 prebuilt/assembled.csv \
    -as prebuilt/cosmos/publish prebuilt/cosmos_os.csv \
    -as prebuilt/powershell-osx-arm64 prebuilt/powershell.csv
```
