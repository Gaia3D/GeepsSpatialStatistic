##############################
# Global Getis-Ord's G

import pysal
from pysal import G
import numpy as np

f = pysal.open(pysal.examples.get_path("stl_hom.dbf"))
y = np.array(f.by_col("HR7984"))

dist_w = pysal.threshold_binaryW_from_shapefile(pysal.examples.get_path('stl_hom.shp'),0.6)
dist_w.transform = "B"

gg = G(y, dist_w)
print gg.G
print gg.EG
print gg.z_norm
print gg.p_norm


##############################
# Local Getis-Ord's G

import pysal
from pysal import G_Local
import numpy as np

f = pysal.open(pysal.examples.get_path("stl_hom.dbf"))
y = np.array(f.by_col("HR7984"))

dist_w = pysal.threshold_binaryW_from_shapefile(pysal.examples.get_path('stl_hom.shp'),0.6)
dist_w.transform = "B"

lg = G_Local(y, dist_w)
print lg.Gs[0]
print lg.z_sim[0]