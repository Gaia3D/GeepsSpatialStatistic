import pysal
import numpy as np

w = pysal.open(pysal.examples.get_path("stl.gal")).read()
f = pysal.open(pysal.examples.get_path("stl_hom.txt"))
y = np.array(f.by_col['HR8893'])

mi = pysal.esda.moran.Moran(y,  w)
"%7.5f" % mi.I
"%7.5f" % mi.EI