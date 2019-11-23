# TODO: clean up and turn into a test

from pathlib import Path
from .mecway import Mecway


FILE = Path("model.liml")


for p in Path().glob("*XX mm.liml"):
    mway = Mecway(p)

    print(f"\n\nAdjusting {mway}\n\n")

    mat = mway.materials["TIG_Plastic"]

    x = x + 2
    new_parts = lines[x].split('"')
    old = float(new_parts[3].split()[0])
    new = old / 0.7 * 0.10
    new_parts = " ".join((f"{new:.3f}", "GPa"))
    new_parts = lines[x].split('"')
    new_parts[3] = " ".join((f"{new:.3f}", "GPa"))
    lines[x] = '"'.join(new_parts)
