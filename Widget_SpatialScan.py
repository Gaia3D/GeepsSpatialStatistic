# -*- coding: utf-8 -*-
from gui.ui_form_spatial_scan import Ui_Form_Parameter as Ui_Form
from Utility import *
from qgis.core import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import math
from math import log
import numpy as np
import time
from bisect import bisect_right


# 지역정보 저장 클래스
class ZoneInfo():
    cent = None
    n = None
    c = None
    def __init__(self, cent, n, c):
        self.cent = cent
        self.n = n
        self.c = c

class Widget_SpatialScan(QWidget, Ui_Form):
    title = "Spatial Scan"
    objectName = "objSpatialScan"

    # 전역변수 설정
    __crrLayerName = None
    __crrIdColumn = None
    __crrTgtColumn = None

    NUM_SIMULATION = 999
    BASE_DS = None
    BASE_DT = None

    N_ST = None
    N_sim = []

    ### 생성자 및 소멸자
    #생성자
    def __init__(self, iface, dockwidget):
        QWidget.__init__(self)
        Ui_Form.__init__(self)
        self.setupUi(self)
        self.progressBar.setVisible(False)
        self.lbl_log.setVisible(False)

        self.__iface = iface
        self.__canvas = iface.mapCanvas()
        self.__dockwidget = dockwidget
        self.__connectAction()

    # 소멸자
    def __del__(self):
        self.disconnectGlobalSignal()

    ### 외부용 함수
    # 위젯이 소멸될 때 전역 이벤트 리스터 연결제거
    def disconnectGlobalSignal(self):
        self.disconnect(self.__canvas, SIGNAL("layersChanged()"), self.__onCanvasLayersChanged)

    # QGIS 레이어 리스트 갱신을 UI에
    def updateGuiLayerList(self):
        layers = self.__canvas.layers()
        layerNameList = []
        bCrrLayerFound = False
        iCrrLayer = 0
        for layer in layers:
            # 벡터가 아닌 레이어 무시
            if layer.type() != QgsMapLayer.VectorLayer:
                continue

            layerName = layer.name()
            layerNameList.append(layerName)
            if (layerName == self.__crrLayerName):
                self.__crrLayerName = layerName
                bCrrLayerFound = True
            if (not bCrrLayerFound):
                iCrrLayer += 1

        self.cmbLayer.clear()
        self.cmbLayer.addItems(layerNameList)


    ### UI 동작처리
    # UI에 이벤트 핸들러 부착
    def __connectAction(self):
        self.connect(self.__canvas, SIGNAL("layersChanged()"), self.__onCanvasLayersChanged)
        self.connect(self.__dockwidget, SIGNAL("visibilityChanged (bool)"), self.__signal_DocWidget_visibilityChanged)
        self.connect(self.cmbLayer, SIGNAL("currentIndexChanged(int)"), self.__onCmbLayerChanged)
        self.connect(self.btnRun, SIGNAL("clicked()"), self.__onRun)

    # UI 동작 정의
    # QGIS의 레이어가 변경된 때
    def __onCanvasLayersChanged(self):
        self.updateGuiLayerList()

    # 위젯의 가시성 변화 시
    def __signal_DocWidget_visibilityChanged(self, visible):
        #self.__resetMaker()
        pass

    # 레이어 선택 콤보 변경시
    def __onCmbLayerChanged(self, index):
        layerName = self.cmbLayer.currentText()
        if (layerName != self.__crrLayerName):
            self.__crrLayerName = layerName
            self.__fillLayerColumn(layerName)

    def getLayerFromName(self, layerName):
        retLayer = None
        for layer in self.__canvas.layers():
            # 벡터가 아닌 레이어 무시
            if layer.type() != QgsMapLayer.VectorLayer:
                continue
            if (layer.name() == layerName):
                retLayer = layer
        return retLayer

    # 선택된 레이어의 컬럼 정보 채우기
    def __fillLayerColumn(self, layerName):
        tgtLayer = self.getLayerFromName(layerName)
        if (not tgtLayer):
            self.cmbCaseColumn.clear()
            self.cmbPopColumn.clear()
        else:
            provider = tgtLayer.dataProvider()
            if provider:
                fields = provider.fields()
                fieldNameList = []
                i = 0; idxIdColumn = 0; idxTgtColumn = 0
                for field in fields:
                    fieldName = field.name()
                    fieldNameList.append(fieldName)
                    if fieldName == self.__crrIdColumn:
                        idxIdColumn = i
                    if fieldName == self.__crrTgtColumn:
                        idxTgtColumn = i
                    i += 1
                self.cmbPopColumn.clear()
                self.cmbPopColumn.addItems(fieldNameList)
                self.cmbPopColumn.setCurrentIndex(idxIdColumn)
                self.cmbCaseColumn.clear()
                self.cmbCaseColumn.addItems(fieldNameList)
                self.cmbCaseColumn.setCurrentIndex(idxIdColumn)

    # Run 버튼 클릭시: 실행에 필요한 조건이 다 입력되었는지 확인
    def __onRun(self):
        ### 입력 데이터 검사
        # 선택된 레이어 이름 확보
        layerName = self.cmbLayer.currentText()

        if (not layerName) or (layerName == ""):
            alert(u"분석할 레이어를 선택하셔야 합니다.")
            return

        # 존재하는 레이어인지 확인
        srcLayer = None
        for layer in self.__canvas.layers():
            if (layer.name() == layerName) and (layer.type() == QgsMapLayer.VectorLayer):
                srcLayer = layer
                break

        if not srcLayer:
            alert(u"선택된 레이어가 없습니다.")
            return

        popColumnName = self.cmbPopColumn.currentText()
        popColumn = srcLayer.dataProvider().fields().field(popColumnName)
        if not popColumn:
            alert(u"선택된 Population 컬럼이 없습니다.")
            return

        caseColumnName = self.cmbCaseColumn.currentText()
        caseColumn = srcLayer.dataProvider().fields().field(caseColumnName)
        if not caseColumn:
            alert(u"선택된 Case 컬럼이 없습니다.")
            return

        if (popColumnName == caseColumnName):
            rc = alert(u"ID 와 Data 컬럼이 같습니다.\n계속하시겠습니까?", QMessageBox.Question)
            if (rc != QMessageBox.Yes):
                return

        try:
            self.NUM_SIMULATION = long(self.edtNumSimul.text())
        except:
            alert(u"Number of monte carlo simulation이 잘못되었습니다.")
            self.edtNumSimul.setText("{0}".format(self.NUM_SIMULATION))
            return


        if self.__runSpatialScan(srcLayer, popColumnName, caseColumnName, self.NUM_SIMULATION):
            alert(u"Spatial Scan 분석 완료")
        else:
            alert(u"Spatial Scan 분석 실패")

    # Spatial Scan 수행
    def __runSpatialScan(self, oLayer, popColumnName, caseColumnName, numSimul):

        try:
            # ID 리스트 확보
            oIdList = oLayer.allFeatureIds()
            if len(oIdList) == 0:
                raise Exception("레이어에 객체가 없습니다.")

            MIN_RADIUS = min(oLayer.extent().width(), oLayer.extent().width()) / 50
            TIC_DIST = min(oLayer.extent().width(), oLayer.extent().width()) / 200

            # Collect source data
            zoneDic = {} # [0]: centroid, [1]: n, [2]: c
            sum_n = 0 # sum of populations
            sum_c = 0 # sum of cases

            self.progressBar.setVisible(True)
            self.lbl_log.setVisible(True)

            self.progressBar.setMaximum(len(oIdList))
            self.lbl_log.setText(u"지역정보 수집중...")
            for i, zone in enumerate(oIdList):
                self.progressBar.setValue(i)
                forceGuiUpdate()

                iFeature = oLayer.getFeatures(QgsFeatureRequest(zone)).next()
                iCent = iFeature.geometry().centroid()
                n = iFeature[popColumnName]
                c = iFeature[caseColumnName]
                zoneDic[zone] = ZoneInfo(iCent, n, c)
                sum_n += n
                sum_c += c

            # 결과 표시용 레이어 만들기
            flagDrawCircle = self.chkZoneCircle.checkState() & Qt.Checked
            flagDrawTick = self.chkZoneTick.checkState() & Qt.Checked

            resultLayer = None
            if flagDrawCircle or flagDrawTick:
                resultLayer = self.__createResultLayer(oLayer)

            ################################
            # 첫 지역 산출
            self.lbl_log.setText(u"Calculate 1st zone...")
            fstZone, fstCent, fstRadius, fstLR, fstNearZone_list = scan(zoneDic, oIdList, MIN_RADIUS)
            self.drawResult(resultLayer, zoneDic, 1, fstZone, fstCent, fstRadius, fstNearZone_list, TIC_DIST)

            #################################
            # 두번째 지역 산출
            self.lbl_log.setText(u"Calculate 2nd zone...")

            # 처음 찾아진 지역을 제외한 지역 리스트 구축
            sndZone_list = []
            for zone in oIdList:
                if fstNearZone_list.count(zone) == 0:
                    sndZone_list.append(zone)

            # 지역 산출
            sndZone, sndCent, sndRadius, sndLR, sndNearZone_list = scan(zoneDic, sndZone_list, MIN_RADIUS)
            self.drawResult(resultLayer, zoneDic, 2, sndZone, sndCent, sndRadius, sndNearZone_list, TIC_DIST)

            #################################
            # 세번째 지역 산출
            self.lbl_log.setText(u"Calculate 3rd zone...")

            # 두번째 찾아진 지역을 제외한 지역 리스트 구축
            trdZone_list = []
            for zone in sndZone_list:
                if sndNearZone_list.count(zone) == 0:
                    trdZone_list.append(zone)

            # 지역 산출
            trdZone, trdCent, trdRadius, trdLR, trdNearZone_list = scan(zoneDic, trdZone_list, MIN_RADIUS)
            self.drawResult(resultLayer, zoneDic, 3, trdZone, trdCent, trdRadius, trdNearZone_list, TIC_DIST)


            ################################
            # Hypothesis Testing

            # Progress 생성
            self.progressBar.setVisible(True)
            self.progressBar.setMaximum(numSimul)

            orgZone_list = oIdList

            fst_sim_LR = [fstLR]
            snd_sim_LR = [sndLR]
            trd_sim_LR = [trdLR]
            for iSim in range(numSimul):
                self.progressBar.setValue(iSim)
                self.lbl_log.setText(u"Monte-Carlo Simulating({0}/{1})...".format(iSim, numSimul))
                forceGuiUpdate()

                # Make Monte-Carlo event by zone's n rate
                randList = np.random.rand(sum_c)*sum_n
                sim_zoneDic = zoneDic.copy()
                popTotal = 0
                for zone in orgZone_list:
                    popTotal += zoneDic[zone].n
                    index = np.where(randList <= popTotal)
                    c = len(randList[index])
                    sim_zoneDic[zone].c = c
                    randList = np.delete(randList, index)

                # 혹시 남은 지역이 있는 경우 마지막 지역으로
                if len(randList) > 0:
                    zone = orgZone_list[-1]
                    c = len(randList)
                    sim_zoneDic[zone].c = c


                # 첫 지역 산출
                sim_fstZone, sim_fstCent, sim_fstRadius, sim_fstLR, sim_fstNearZone_list = scan(sim_zoneDic, orgZone_list, MIN_RADIUS)
                fst_sim_LR.append(sim_fstLR)

                # 처음 찾아진 지역을 제외한 지역 리스트 구축
                sndZone_list = []
                for zone in orgZone_list:
                    if sim_fstNearZone_list.count(zone) == 0:
                        sndZone_list.append(zone)

                # 두번째 지역 산출
                sim_sndZone, sim_sndCent, sim_sndRadius, sim_sndLR, sim_sndNearZone_list = scan(sim_zoneDic, sndZone_list, MIN_RADIUS)
                snd_sim_LR.append(sim_sndLR)

                # 두번째 찾아진 지역을 제외한 지역 리스트 구축
                trdZone_list = []
                for zone in sndZone_list:
                    if sim_sndNearZone_list.count(zone) == 0:
                        trdZone_list.append(zone)

                # 세번째 지역 산출
                sim_trdZone, sim_trdCent, sim_trdRadius, sim_trdLR, sim_trdNearZone_list = scan(sim_zoneDic, trdZone_list, MIN_RADIUS)
                trd_sim_LR.append(sim_trdLR)


            #########################
            # Calculate p-value
            fst_sim_LR.sort()
            snd_sim_LR.sort()
            trd_sim_LR.sort()

            fst_pos = bisect_right(fst_sim_LR, fstLR)
            fst_p = (1.0 - (float(fst_pos) / float(numSimul+1)))

            snd_pos = bisect_right(snd_sim_LR, sndLR)
            snd_p = (1.0 - (float(snd_pos) / float(numSimul+1)))

            trd_pos = bisect_right(trd_sim_LR, trdLR)
            trd_p = (1.0 - (float(trd_pos) / float(numSimul+1)))

            resString = ("1st p-value:%.3f, 2nd p-value:%.3f, 3rd p-value:%.3f" % (fst_p, snd_p, trd_p))
            self.txtResult.setPlainText(resString)
            self.progressBar.setVisible(False)
            self.lbl_log.setVisible(False)
        except Exception as e:
            alert(e.message)
            return False

        return True

    def drawResult(self, tLayer, zoneDic, grade, zoneID, zoneCent, radius, nearZone_list, tickDist):
        tLayer.startEditing()
        tProvider = tLayer.dataProvider()

        # make near zone list string
        nearZone_str = ""
        for zone in nearZone_list:
            if nearZone_str != "":
                nearZone_str += ","
            nearZone_str += str(zone)

        # Draw circle
        tFeature = QgsFeature(tProvider.fields())
        tFeature.setGeometry(QgsGeometry.fromPolyline(createCircle(zoneCent.vertexAt(0), radius)))
        tFeature.setAttribute(0, zoneID)
        tFeature.setAttribute(1, nearZone_str)
        tFeature.setAttribute(2, grade)
        tProvider.addFeatures([tFeature])

        # Draw Tic
        for zone in nearZone_list:
            cent = zoneDic[zone].cent
            pnt = cent.vertexAt(0)
            geom = QgsGeometry.fromPolyline([QgsPoint(pnt.x()-tickDist, pnt.y()-tickDist), QgsPoint(pnt.x()+tickDist, pnt.y()+tickDist)])
            tFeature.setGeometry(geom)
            tFeature.setAttribute(0, zoneID)
            tFeature.setAttribute(1, zone)
            tFeature.setAttribute(2, grade)
            tProvider.addFeatures([tFeature])
            geom = QgsGeometry.fromPolyline([QgsPoint(pnt.x()+tickDist, pnt.y()-tickDist), QgsPoint(pnt.x()-tickDist, pnt.y()+tickDist)])
            tFeature.setGeometry(geom)
            tFeature.setAttribute(0, zoneID)
            tFeature.setAttribute(1, zone)
            tFeature.setAttribute(2, grade)
            tProvider.addFeatures([tFeature])

        tLayer.commitChanges()
        tLayer.triggerRepaint()
        self.__canvas.refresh()

    # Create Result Layer
    def __createResultLayer(self, orgLayer):
        resultLayerName = "Scan_"+orgLayer.name()

        # 결과 레이어 이미 있는지 확인
        tLayer = None
        layers = self.__canvas.layers()
        for testLayer in layers:
            name = testLayer.name()
            if name != resultLayerName:
                continue
            if testLayer.type() != QgsMapLayer.VectorLayer:
                continue
            tLayer = testLayer

            # 기존 결과 레이어 객체 모두 지우기
            caps = tLayer.dataProvider().capabilities()
            if caps & QgsVectorDataProvider.DeleteFeatures:
                ids = tLayer.allFeatureIds()
                res = tLayer.dataProvider().deleteFeatures(ids)
            break

        if not tLayer:
            crs = orgLayer.crs()
            tLayerOption = "{0}?crs={1}&index=yes".format("LineString", crs.authid())
            tLayer = QgsVectorLayer(tLayerOption, resultLayerName, "memory")
            tProvider = tLayer.dataProvider()
            tLayer.startEditing()
            tProvider.addAttributes([QgsField("ZoneID", QVariant.Int),
                         QgsField("ScannedZone", QVariant.String),
                         QgsField("Grade", QVariant.Int)
            ])

            # Apply symbol
            symbol = QgsSymbolV2.defaultSymbol(QGis.Line)
            symbol.setColor(QColor(255,0,0))
            category1 = QgsRendererCategoryV2(1, symbol, "1st Scanned")

            symbol = QgsSymbolV2.defaultSymbol(QGis.Line)
            symbol.setColor(QColor(0,0,255))
            category2 = QgsRendererCategoryV2(2, symbol, "2nd Scanned")

            symbol = QgsSymbolV2.defaultSymbol(QGis.Line)
            symbol.setColor(QColor(0,255,0))
            category3 = QgsRendererCategoryV2(3, symbol, "3rd Scanned")

            categories = [category1, category2, category3]
            renderer = QgsCategorizedSymbolRendererV2("Grade", categories)
            tLayer.setRendererV2(renderer)

            tLayer.commitChanges()
            QgsMapLayerRegistry.instance().addMapLayer(tLayer)
            self.__canvas.refresh()

        return tLayer

# Likelihood Ratio Calculation function
def calcLR(N, C, n, c):
    if c == 0:
        LR = 0
        return LR

    N = float(N)
    C = float(C)
    n = float(n) # Population of Zone
    c = float(c) # Case of Zone
#    LR = (((c/n)**c) * ((1.0-(c/n))**(n-c)) * (((C-c)/(N-n))**(C-c)) * ((1-((C-c)/(N-n)))**((N-n)-(C-c)))) \
#         / (((C/N)**C) * ((1-(C/N))**(N-C)))
    # ((C/N)**C) 값의 너무 작아져 실수표현시 항상 0.0 이되어 문제 --> log로 극복
    log_LR = ( c*log(c/n) + (n-c)*log(1.0-(c/n)) + (C-c)*log((C-c)/(N-n)) + ((N-n)-(C-c))*log(1-(C-c)/(N-n)) ) \
             - ( C*log(C/N) + (N-C)*log(1-C/N) )
    LR = math.e ** log_LR
    return LR

# 주어진 지역에 대해 LR이 가장 큰 지역과 주변이 합쳐져서 가장 LR이 큰 지역관련 정보 계산
def scan(zoneDic, zoneList, minRadius):
    # lambda function for sort by second item
    getSecond = lambda item: item[1]

    # return value
    resZoneID = None
    resZoneCent = None
    resRadius = None
    resLR = None
    resNearZone_list = []

    # zoneList에 있는 지역의 모집단수(N)과 케이스수(C) 확보
    N = 0
    C = 0
    for zone in zoneList:
        N += zoneDic[zone].n
        C += zoneDic[zone].c

    # 가장 LR이 큰 지역 찾기
    LR_list = [[zone, calcLR(N, C, zoneDic[zone].n, zoneDic[zone].c)] for zone in zoneList]
    LR_list.sort(key=getSecond, reverse=True)
    resZoneID = LR_list[0][0]
    resLR = LR_list[0][1]
    resZoneCent = zoneDic[resZoneID].cent

    # 찾은 지역으로 부터 거리순 소팅
    dist_list = []
    for zone in zoneList:
        iCent = zoneDic[zone].cent
        if zone == resZoneID:
            continue
        dist = resZoneCent.distance(iCent)
        dist_list.append([zone, dist])
    dist_list.sort(key=getSecond)

    # 절반이 될 때까지 합치며 진행한 중에 가장 LR이 큰 지역 찾기
    sub_n = zoneDic[resZoneID].n
    sub_c = zoneDic[resZoneID].c
    resNearZone_list = [resZoneID]
    tempLR_list = [[resZoneID, resLR]]
    for info in dist_list:
        if sub_n >= (N/2.0):
            break
        zone = info[0]
        resNearZone_list.append(zone)
        sub_n += zoneDic[zone].n
        sub_c += zoneDic[zone].c
        tempLR = calcLR(N, C, sub_n, sub_c)
        tempLR_list.append([zone, tempLR])
    tempLR_list.sort(key=getSecond, reverse=True)
    edgeZone = tempLR_list[0][0]
    edgeCent = zoneDic[edgeZone].cent

    # 합쳐진 지역의 LR을 반환
    resLR = tempLR_list[0][1]

    # 합쳐진 지역에 대한 정보 추출
    if resZoneID == edgeZone:
        resRadius = minRadius
    else:
        resRadius = resZoneCent.distance(edgeCent)
    ii = resNearZone_list.index(edgeZone)
    resNearZone_list = resNearZone_list[ : ii+1]

    # 최종 결과 반환
    return (resZoneID, resZoneCent, resRadius, resLR, resNearZone_list)

# 중심과 반경으로 원 그리기
def createCircle(center, radius):
    retPointList = []

    centerX = center.x()
    centerY = center.y()
    angleList = np.linspace(0, math.pi*2, 60)

    for angle in angleList:
        crrX = centerX + math.sin(angle)*radius
        crrY = centerY + math.cos(angle)*radius
        retPointList.append(QgsPoint(crrX, crrY))
    return retPointList
