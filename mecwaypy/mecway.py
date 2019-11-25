from __future__ import annotations
from typing import Optional, MutableSequence, Dict
from dataclasses import dataclass, field, InitVar
from pathlib import Path


def _search_lines(lines, needle, err, start=0):
    for x, line in enumerate(lines, start):
        if needle in line:
            return x, needle
    else:
        raise err


class MecwayException(Exception):
    pass


class LastMaterialException(MecwayException):
    pass


class AttrException(MecwayException):
    pass


class TagException(MecwayException):
    pass


def _get_material_names(lines):
    start = 0
    while True:
        try:
            slc = _material_slice(lines[start:], None, start)
            mat_lines = lines[slc]
            yield _get_material_name(mat_lines)
            start = slc.stop
        except LastMaterialException:
            break


def _get_material_name(mat_lines):
    try:
        return mat_lines[0].split('"')[1]
    except IndexError as e:
        raise AttrException("<mat name=...>") from e


def _get_set_attribute(lines, attr, value=None):
    for line_idx, line in enumerate(lines):
        if attr in line:
            split_tag = line.split('"')
            iter_split_tag = iter(split_tag)
            for x, split in enumerate(iter_split_tag, 1):
                if f"{attr}=" in split and (x % 2):
                    if value is None:
                        # get
                        return next(iter_split_tag)
                    else:
                        # set
                        split_tag[x] = value
                        lines[line_idx] = '"'.join(split_tag)
                        return
    else:
        raise AttrException(f"{attr}=...>")


def _set_attribute(lines, attr, value):
    _get_set_attribute(lines, attr, value)


def _get_attribute(lines, attr):
    return _get_set_attribute(lines, attr)


def _search_material_start(lines, name=None, start=0):
    try:
        if name:
            return _search_lines(lines, f'<mat name="{name}">', TagException(f'<mat name="{name}">'), start)
        else:
            return _search_lines(lines, f'<mat name="', TagException(f"<mat>"), start)
    except TagException as e:
        raise LastMaterialException()


def _search_material_end(lines, start=0):
    return _search_lines(lines, '</mat>', TagException("</mat>"), start)


def _material_slice(lines, name=None, start=0):
    mat_start, _ = _search_material_start(lines, name, start=start)
    mat_end, _ = _search_material_end(lines[mat_start-start:], start=mat_start)
    return slice(mat_start, mat_end + 1)


@dataclass
class Material:
    name: str
    mway: Mecway

    @property
    def slice(self):
        return _material_slice(self.mway.lines, self.name)

    @property
    def lines(self):
        return self.mway.lines[self.slice]

    @lines.setter
    def lines(self, lines):
        self.mway.lines[self.slice] = lines

    def set_param(self, param: str, value: str):
        lines = self.lines
        _set_attribute(lines, param, value)
        self.lines = lines

    def get_param(self, param: str):
        return _get_attribute(self.lines, param)


@dataclass
class Materials:
    mway: Mecway
    _dict: Dict[str, Material] = field(init=False, default_factory=dict)

    def __post_init__(self):
        for name in _get_material_names(self.mway.lines):
            self[name] = Material(name, self.mway)

    def __getitem__(self, name):
        return self._dict[name]

    def __setitem__(self, name, mat):
        self._dict[name] = mat


@dataclass
class Mecway:
    path: Path
    target: InitVar[Optional[Path]] = None
    lines: MutableSequence[str] = field(repr=False, init=False)

    def __post_init__(self, target):

        with self.path.open('r') as mway:
            self.lines = mway.readlines()

        if target:
            self.path = target

    def save(self):

        with self.path.open('w') as mway:
            mway.writelines(self.lines)

    @property
    def materials(self):

        try:
            return self._mats
        except AttributeError:
            mats = self._mats = Materials(self)
            return mats
