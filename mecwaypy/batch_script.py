import itertools
import pathlib
from pathlib import Path
from .mecway import Mecway

TARGET = "comp E {e_comp:d} ksi plastic E {e_plastic_pctg}% TIG E {e_tig_pctg}%.liml"

FILE = Path("model.liml")
E_PLASTIC = 2.47  # GPa
E_COMPOSITE = 5600  # ksi

PLASTIC_RNG = range(70, 95, 5)  # %
CMPST_RNG = range(E_COMPOSITE-200, E_COMPOSITE+300, 100)  # ksi
TIG_RNG =  range(10, 30, 5)  # %


def gen_mecway_combos():
    model = Mecway(pathlib.Path(FILE))
    for composite, plastic, tig in itertools.product(CMPST_RNG, PLASTIC_RNG, TIG_RNG):
        target = pathlib.Path(TARGET.format(e_plastic_pctg=plastic, e_comp=composite, e_tig_pctg=tig))
        p = f"{E_PLASTIC * plastic / 100:.3f} GPa"
        t = f"{E_PLASTIC * plastic / 100 * tig / 100:.3f} GPa"
        c = f"{composite:d} ksi"
        with model.copy(target) as m:
            m.materials["PlasticWalls"].set_param("youngsmodulus", p)
            m.materials["PlasticWallsWithSlits"].set_param("youngsmodulus", p)
            m.materials["CompositeMaterial"].set_param("youngsmodulus", c)
            m.materials["TIG_Plastic"].set_param("youngsmodulus", t)
            csv = str(m.path.with_suffix(".csv").name)
            for x, line in enumerate(m.lines):
                if "<saveonsolve filename=" in line:
                    m.lines[x] = f'    <saveonsolve filename="{csv}" />'
