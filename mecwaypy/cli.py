from multiprocessing import Pool
from multiprocessing.pool import AsyncResult
from pathlib import Path
import subprocess as sp
import os
from typing import Iterable, Optional, Union, Iterator
from mecwaypy.mecway import MecwayException


class SolveException(MecwayException):
    pass


MECWAY_EXE_REL = r"Mecway\Mecway8\mecway.exe"

try:
    MECWAY_EXE_PATH = (Path(os.environ["PROGRAMFILES"]) / MECWAY_EXE_REL).resolve(strict=True)
except FileNotFoundError as e:
    raise SolveException("mecway executable not found") from e
except KeyError as e:
    raise SolveException("Program Files environment variable not found") from e


def solve(liml_path: Union[Path, str], window:bool=False, **kwargs) -> sp.CompletedProcess:
    args = [f'{MECWAY_EXE_PATH!s}', f'{liml_path!s}']
    if not window:
        args.append("solve")
    result = sp.run(args, **kwargs)
    return result


def solve_multi(path_or_paths: Union[Path, str, Iterable[Union[Path, str]]]=(), glob: Optional[str]=None, n: int=2, **kwargs):
    # get an iterable of Path objects
    paths = (Path(path_or_paths),) if isinstance(path_or_paths, (Path, str)) else (Path(p) for p in path_or_paths)

    # get a Path object iterator
    iter_paths: Iterator[Path]
    if glob:
        iter_paths = (f for p in paths for f in Path(p).glob(glob))
    else:
        iter_paths = iter(paths)

    pool = Pool(processes=n)
    for p in iter_paths:
        if p.suffix!=".liml":
            raise SolveException(f"invalid file type: {p.suffix}")
        pool.apply_async(solve, [p], kwds=kwargs, callback=handle_result)
    pool.close()
    pool.join()


def handle_result(result: AsyncResult) -> None:
    result.successful()
    print(result.get())
