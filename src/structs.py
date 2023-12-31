import typing as t

import attrs


@attrs.define(frozen=True, slots=True)
class LaunchInfo:
    dll: str
    method: str
    steps: t.Optional[int] = None


@attrs.define(frozen=True, slots=True)
class RunResult:
    method: str
    steps: int
    tests: int
    errors: int
    coverage: float
    total_time_sec: int
    timeouted: bool


Method: t.TypeAlias = str
Class: t.TypeAlias = str
DLL: t.TypeAlias = str


@attrs.define(frozen=True, slots=True)
class ClassMethodsMapping:
    clazz: Class
    methods: list[Method]


@attrs.define(frozen=True, slots=True)
class PrebuiltConfig:
    dll_dir: str
    dlls: dict
