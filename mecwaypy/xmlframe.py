from typing import Any, Union
import pandas as pd
from pandas.core.strings import StringMethods as DFString
from mecwaypy.mecway import TagException, AttrException


LB = "lb"
RB = "rb"
TAG = "tag"
ATTRS="attrs"


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
    if _check((attr_part_end_srs!='"') & (attr_part_end_srs!="")):
        raise TagException("appear to be malformed attribute(s) in tag")
    attrs_df = str_srs.str.split('"', expand=True).replace({None: ""}).iloc[:, :-1]

    # combine parsed and attrs
    result_df = (parsed_df + attrs_df)  # np.nan populated
    result_df.update(parsed_df)
    result_df.update(attrs_df)

    return result_df
