import pathlib
import pytest
from mecwaypy import mecway

TEST_LIML = ""
TEST_FILE = "test.liml"


@pytest.fixture
def mecway_path(tmpdir):
    p = pathlib.Path(tmpdir) /  TEST_FILE
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
