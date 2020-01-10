from dataclasses import dataclass
import xml.etree.ElementTree as xml
from dataclass_xml import DataclassElement


@dataclass
class _MecwayElement(DataclassElement):
    """Parent class for all .liml file elements"""
    pass


@dataclass
class Elset(_MecwayElement, tag="elset"):
    name: str
    color: int
    expanded: bool

    class Elem(_MecwayElement, tag="elem"):
        eid: int
        shape: str
        nodes: str


@dataclass
class Analysis(_MecwayElement, tag="analysis"):
    type: str = "S30"


@dataclass
class Liml(_MecwayElement, tag="liml"):
    version: int = 8

    Elset = Elset

    @dataclass
    class Node(_MecwayElement, tag="node"):
        nid: int
        x: str
        y: str


    @dataclass
    class Mat(_MecwayElement, tag="mat"):
        name: str


    @dataclass
    class ShellMat(Mat):

        @dataclass
        class Geometric(_MecwayElement, tag="geometric"):
            thickness: str
            type: str = "Plate"

        @dataclass
        class Mechanical(_MecwayElement, tag="mechanical"):
            youngsmodulus: str
            poissonsratio: str
            type: str = "Isotropic"

        @dataclass
        class Density(_MecwayElement, tag="density"):
            density: str
            type: str = "Simple"


    @dataclass
    class Solution(_MecwayElement, tag="solution"):

        Analysis = Analysis
        Elset = Elset
