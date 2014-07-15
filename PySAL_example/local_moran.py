import pysal
import numpy as np

np.random.seed(10)
w = pysal.open(pysal.examples.get_path("desmith.gal")).read()
f = pysal.open(pysal.examples.get_path("desmith.txt"))
y = np.array(f.by_col['z'])
lm = pysal.Moran_Local(y, w, transformation = "r", permutations = 99)
lm.q
lm.p_z_sim[0]