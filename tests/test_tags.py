from mecwaypy.tags import Liml, Analysis, Elset


def test_liml_tags():
    liml = Liml()
    liml.append(Analysis())
    liml.append(Elset(name="Default", color=-6710887, expanded=True))
