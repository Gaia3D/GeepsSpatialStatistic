############################
## Global Moran's I
import pysal
import numpy as np
from pysal import Moran

w = pysal.open(pysal.examples.get_path("stl.gal")).read()
f = pysal.open(pysal.examples.get_path("stl_hom.txt"))
y = np.array(f.by_col['HR8893'])

mi = Moran(y,  w)
"%7.5f" % mi.I
"%7.5f" % mi.EI


############################
## Local Moran's I
import pysal
import numpy as np
from pysal import Moran_Local

np.random.seed(10)
w = pysal.open(pysal.examples.get_path("desmith.gal")).read()
f = pysal.open(pysal.examples.get_path("desmith.txt"))
y = np.array(f.by_col['z'])

lm = Moran_Local(y, w, transformation = "r", permutations = 99)
lm.q
lm.p_z_sim[0]