############################
## Global Moran's I
import pysal
import numpy as np

w = pysal.open(pysal.examples.get_path("stl.gal")).read()
f = pysal.open(pysal.examples.get_path("stl_hom.txt"))
y = np.array(f.by_col['HR8893'])

mi = pysal.esda.moran.Moran(y,  w)
"%7.5f" % mi.I
"%7.5f" % mi.EI


############################
## Local Moran's I
import pysal
import numpy as np

np.random.seed(10)
w = pysal.open(pysal.examples.get_path("desmith.gal")).read()
f = pysal.open(pysal.examples.get_path("desmith.txt"))
y = np.array(f.by_col['z'])
lm = pysal.Moran_Local(y, w, transformation = "r", permutations = 99)
lm.q
lm.p_z_sim[0]


############################
## Moran's I with QGIS

from pysal import W, Moran, Moran_Local
import numpy as np
import qgis
from qgis.core import *
from qgis.gui import QgsMessageBar
from PyQt4.QtGui import QProgressBar
from PyQt4.QtCore import *

# 전역변수 설정
NEIGHBOR_DIST = 100
VALUE_FIELD = "X"
NAME_FIELD =  "Y"
SIG_LEVEL = 0.1
WEIGHT_MODE = "QUEEN" #DIST, QUEEN, ROOK

gErrorMsg = ""

try:
    print u"[Moran's I 테스트] 인접판단기준: %f" % NEIGHBOR_DIST

    layer = qgis.utils.iface.activeLayer()
    if not layer:
        gErrorMsg = u"레이어를 먼저 선택해야 합니다."
        raise UserWarning # 종료

    layerName = layer.name()
    layerType = layer.geometryType();
    layerTypeName = ""

    if layerType == QGis.Point:
        layerTypeName = "Point"
    elif layerType == QGis.Line:
        layerTypeName = "Line"
    elif layerType == QGis.Polygon:
        layerTypeName = "Polygon"
    else:
        layerTypeName = "Unknown"

    crs = layer.crs()

    print u"현재 선택된 레이어: %s" % layerName

    # 선형은 처리 불기
    if layerType == QGis.Line:
        gErrorMsg =  u"Line 형태의 레이어는 지원하지 않습니다."
        raise UserWarning # 종료

    # ID 리스트 확보
    ids = layer.allFeatureIds()

    # Weight
    neighbors  = {}
    weights = {}

    # Data
    dataList = []

    # Progress 생성
    progressMessageBar = iface.messageBar().createMessage(u"공간상관관계 계산중...")
    progress = QProgressBar()
    progress.setMaximum(len(ids))
    progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
    progressMessageBar.layout().addWidget(progress)
    iface.messageBar().pushWidget(progressMessageBar, iface.messageBar().INFO)

    iPrg = 0;
    for i in ids:
        iFeature = layer.getFeatures(QgsFeatureRequest(i)).next()
        iGeom = iFeature.geometry()
        iRowNeighbors = []
        iRowWeights = []

        iPrg += 1
        progress.setValue(iPrg + 1)

        for j in ids:
            jFeature = layer.getFeatures(QgsFeatureRequest(j)).next()
            jGeom = jFeature.geometry()

            if i == j: # 같은 지역인 경우
                dist = 0.0
            else:
                if WEIGHT_MODE == "DIST":
                    dist = iGeom.distance(jGeom)
                    if dist != 0.0 and dist <= NEIGHBOR_DIST:
                        iRowNeighbors.append(j)
                        iRowWeights.append(1)
                        #iRowWeights.append(1.0/dist)

                elif WEIGHT_MODE == "QUEEN":
                    if iGeom.touches(jGeom):
                        iRowNeighbors.append(j)
                        iRowWeights.append(1)

                elif WEIGHT_MODE == "ROOK":
                    pass # 방법을 모르겠다!!!
                else:
                    gErrorMsg = u"잘못된 WEIGHT_MODE: "+WEIGHT_MODE
                    raise UserWarning

        neighbors[i] = iRowNeighbors
        weights[i] = iRowWeights
        val = iFeature[VALUE_FIELD]
        dataList.append(val)

    # Progress 제거
    iface.messageBar().clearWidgets()

    w = W(neighbors, weights)
    print w.full()

    y = np.array(dataList)
    #print y

    # Moran's I 계산
    mi = Moran(y, w)

    # 결과 출력
    moran_i_res = u"Moran's I 값: {0:.2f}, z_norm: {1:.2f}, p_norm: {2:.5f} 이므로 ".format(mi.I, mi.z_norm, mi.p_norm)
    if mi.I > mi.EI:
        moran_i_res += u"양의 공간자기상관임. 비슷한 유형의 자료가 모여 있음"
    elif mi.I < mi.EI:
        moran_i_res += u"음의 공간자기상관임. 상이한 유형의 자료가 모여 있음"
    else:
        moran_i_res += u"공간자기상관 없음. 완전히 랜덤하게 자료가 분포됨"

    # Local Moran
    lm = Moran_Local(y, w, transformation = "r")

    # Memory Layer
    print layerTypeName

    # crs를 찾기에 실패함
    tLayerOption = "{0}?crs={1}&index=yes".format(layerTypeName, crs.authid())
    print tLayerOption
    tLayer = QgsVectorLayer(tLayerOption, "Moran_"+layerName, "memory")
    tProvider = tLayer.dataProvider()
    tLayer.startEditing()
    tProvider.addAttributes([QgsField("NAME", QVariant.String), QgsField("Z", QVariant.Double), QgsField("P", QVariant.Double)])

    for i in range(len(ids)):
        id = ids[i]
        oFeature = layer.getFeatures(QgsFeatureRequest(id)).next()
        name = oFeature[NAME_FIELD]

        if lm.p_sim[i] <= SIG_LEVEL:
            tFeature = QgsFeature(tProvider.fields())
            tFeature.setGeometry(oFeature.geometry())
            tFeature.setAttribute(0, name)
            tFeature.setAttribute(1, float(lm.z_sim[i]))
            tFeature.setAttribute(2, float(lm.p_sim[i]))
            tProvider.addFeatures([tFeature])
    tLayer.commitChanges()
    tLayer.updateExtents()

    QgsMapLayerRegistry.instance().addMapLayer(tLayer)
    #qgis.utils.iface.mapCanvas().setExtent(tLayer.extent())
    qgis.utils.iface.mapCanvas().refresh()

    iface.messageBar().pushMessage("Complet", moran_i_res)

except KeyError, e:
    iface.messageBar().pushMessage("Error", str(e) + u" 필드를 찾지 못함", level=QgsMessageBar.CRITICAL)

# 오류 메시지 표시
except UserWarning:
    iface.messageBar().pushMessage("Error", gErrorMsg, level=QgsMessageBar.CRITICAL)