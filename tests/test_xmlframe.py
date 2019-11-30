from mecwaypy.xmlframe import _parsed_df, TAG, LB, RB
import pandas as pd
import pytest


@pytest.mark.parametrize("txt", [
    """<q attr1="a" attr2="b">
    <p attr3="c"/>
    <v attr4="d"/>
    </q>""",

    """<q>
    <p/>
    <v/>
    </q>""",
])
def test_parsed_df(txt):
    df=pd.DataFrame(txt.split("\n"), columns=['a'])
    parsed_df = _parsed_df(df)
    idxs = range(4)
    tags = "qpvq"
    assert list(parsed_df[TAG].iteritems())==list(zip(idxs, tags))
    left_brackets = "<", "<", "<", "</"
    assert list(parsed_df[LB].iteritems())==list(zip(idxs, left_brackets))
    right_brackets = ">", "/>", "/>", ">"
    assert list(parsed_df[RB].iteritems())==list(zip(idxs, right_brackets))
    ...
