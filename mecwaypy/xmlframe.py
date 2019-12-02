from __future__ import annotations

from dataclasses import dataclass, field, InitVar
from typing import Any, Union, Dict, Optional, KeysView
import pandas as pd
from pandas.core.strings import StringMethods as DFString
from mecwaypy.mecway import TagException, AttrException


LB = "lb"
RB = "rb"
TAG = "tag"


def _check(s: Any) -> bool:
    """Truthy check an atomic or a pd.Series"""
    if isinstance(s, pd.Series):
        return s.any()
    return s


def _validate(xml_str: Union[str, DFString]):
    """Confirm a str or str-like conforms to XML (with or without attributes) format.

    Note: Attribute values must be defined with double quotations.
    """
    # check start and end of tag
    if _check(xml_str[0] != "<") and _check(xml_str[-1] != ">"):
        raise TagException("no tag")
    # check double quote pairs indicating attributes
    if _check(xml_str.count('"') % 2):
        raise AttrException('odd number of double quotations (")')


def _parsed_df(xml_df: pd.DataFrame):
    """New pd.DataFrame containing parsed XML contents."""
    parsed_df = pd.DataFrame(index=xml_df.index)

    col0 = xml_df.columns[0]
    str_srs: pd.Series = xml_df[col0].str.strip()
    _validate(str_srs.str)
    str_srs = str_srs.str[1:-1].str.strip()

    # right brackets
    parsed_df[RB] = ">"
    end_char = str_srs.str[-1]
    end_slash_filter = end_char=="/"
    parsed_df[RB].update(end_char[end_slash_filter] + parsed_df[RB])
    # remove any right slashes (atomic tags)
    str_srs.update(str_srs[end_slash_filter].str[:-1])

    # left brackets
    parsed_df[LB] = "<"
    start_char = str_srs.str[0]
    start_slash_filter = start_char=="/"
    parsed_df[LB].update(parsed_df[LB] + start_char[start_slash_filter])
    # remove any left slashes (end tags)
    str_srs.update(str_srs[start_slash_filter].str[1:])

    # break off tag names
    str_srs = str_srs.str.strip()
    iter_tag_attr_columns = (col for _, col in str_srs.str.strip().str.split(" ", 1, expand=True).iteritems())
    parsed_df[TAG], *rest = iter_tag_attr_columns
    try:
        str_srs = rest[0].replace({None:""})
    except IndexError:
        str_srs.at[:] = ""

    # split attributes into names and values
    attr_part_end_srs = str_srs.str[-1:]
    if _check(-attr_part_end_srs.isin(['"', ""])):
        raise TagException("appear to be malformed attribute(s) in tag")
    attrs_df = str_srs.str.split('"', expand=True).replace({None: ""}).iloc[:, :-1].apply(lambda srs: srs.str.strip())
    # do away with attribute name equal signs and space
    for attr_col, attr_label_srs in attrs_df.iloc[:,0::2].iteritems():
        attrs_df[attr_col] = attr_label_srs.str.split("=", expand=True)[0].str.strip()
        attrs_df[attr_col].name = attr_col

    # combine parsed and attrs
    result_df = (parsed_df + attrs_df)  # np.nan populated
    result_df.update(parsed_df)
    result_df.update(attrs_df)

    return result_df


def _gen_tag_df(tag: str, parsed_df: pd.DataFrame):
    tag_start_idx = parsed_df.index[(parsed_df[TAG] == tag) & (parsed_df[LB] == "<")]
    tag_stop_idx = parsed_df.index[(parsed_df[TAG] == tag) & ((parsed_df[LB] == "</") | (parsed_df[LB] == "/>"))]
    if tag_start_idx.size != tag_stop_idx.size:
        raise TagException(f"{tag!r} tag start end mismatch")
    if _check(tag_stop_idx < tag_start_idx):
        raise TagException(f"{tag!r} tag start end mismatch")
    for start, stop in zip(tag_start_idx, tag_stop_idx):
        yield parsed_df.loc[start:stop, :]


class TagSeries(pd.Series):
    def __new__(cls, srs: pd.Series) -> TagSeries:
        obj = super().__new__(cls, srs)
        return obj


@dataclass
class TagGroup:
    tag: str
    key_attr: str = field(repr=False)
    keys: KeysView = field(init=False)
    map: Dict[str, TagSeries] = field(init=False, repr=False, default_factory=dict)
    df: pd.DataFrame = field(repr=False, init=False, default_factory=pd.DataFrame)
    xml_df: InitVar[Optional[pd.DataFrame]] = None

    def __post_init__(self, xml_df: Optional[pd.DataFrame]):
        self.keys = self.map.keys()

        parsed_df = _parsed_df(xml_df)
        for tag_df in _gen_tag_df(self.tag, parsed_df):
            attr_srs = pd.Series()
            for col_num in range(0, len(tag_df), 2):
                partial_attr_srs = tag_df.iloc[:, col_num:col_num + 2].set_index(col_num).iloc[:, 0]
                attr_srs.append(partial_attr_srs[partial_attr_srs != ""])
            key = attr_srs[self.key_attr]
            attr_srs.name = key
            self.map[key] = TagSeries(attr_srs)
            self.df = self.df.join(attr_srs, how="outer")
