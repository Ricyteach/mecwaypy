import itertools
import pathlib
import pytest
from mecwaypy import mecway

TEST_LIML = """<mat name="mat1">
<attributes1 attr1="a" attr2="b" /> 
<attributes2 attr3="x" attr4="y" /> 
</mat>
<mat name="mat2">
<attributes1 attr1="a" attr2="b" /> 
<attributes2 attr3="x" attr4="y" /> 
</mat>"""

TEST_FILE = "test.liml"


@pytest.fixture
def mecway_path(tmpdir):
    p = pathlib.Path(tmpdir) / TEST_FILE
    with p.open("w") as f:
        f.write(TEST_LIML)
    return p


@pytest.fixture
def mecway_obj(mecway_path):
    return mecway.Mecway(mecway_path)


@pytest.fixture
def materials_obj(mecway_obj):
    return mecway_obj.materials


def test_mecway(mecway_obj):
    assert mecway_obj


def test_materials(materials_obj):
    assert materials_obj


@pytest.mark.parametrize("name", [
    "mat1", "mat2"
])
def test_material(materials_obj, name):
    assert materials_obj[name]


@pytest.mark.parametrize("attr, name", [
    *itertools.product(["attr1", "attr2", "attr3", "attr4"], ["mat1", "mat2"])
])
def test_attr(materials_obj, name, attr):
    assert materials_obj[name].get_param(attr)


# TODO: attr writing tests