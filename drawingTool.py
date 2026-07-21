from qgis.PyQt.QtCore import pyqtSignal, Qt, QTimer
from qgis.PyQt.QtGui import QCursor, QPixmap, QColor
from qgis.core import (
    QgsWkbTypes,
    QgsPointXY,
    Qgis,
    QgsSnappingConfig,
    QgsPointLocator,
    QgsProject,
    QgsTolerance,
    QgsRectangle,
    QgsVectorLayer,
    QgsFeatureRequest,
)
from qgis.gui import QgsMapTool, QgsMapToolPan, QgsRubberBand


class DrawingTool(QgsMapTool):
    pointAdded = pyqtSignal(object)
    drawingFinished = pyqtSignal(object)
    canceled = pyqtSignal()
    mouseMoved = pyqtSignal(object)
    drawingEnded = pyqtSignal()

    def __init__(self, canvas, geomType="polygon"):
        super().__init__(canvas)
        self.canvas = canvas
        self.points = []
        self.isDrawing = False
        self._drawingEnded = False
        self._origSnapConfig = None
        self._panTool = None
        self.geomType = geomType

        try:
            _point_geom = Qgis.GeometryType.Point
        except AttributeError:
            _point_geom = QgsWkbTypes.GeometryType.PointGeometry

        try:
            _line_geom = Qgis.GeometryType.Line
        except AttributeError:
            _line_geom = QgsWkbTypes.GeometryType.LineGeometry

        try:
            _poly_geom = Qgis.GeometryType.Polygon
        except AttributeError:
            _poly_geom = QgsWkbTypes.GeometryType.PolygonGeometry

        self._point_geom = _point_geom
        self._line_geom = _line_geom
        self._poly_geom = _poly_geom

        if self.geomType == "point":
            self.rubberBand = QgsRubberBand(self.canvas, _point_geom)
            self.rubberBand.setIcon(QgsRubberBand.IconType.ICON_CIRCLE)
            self.rubberBand.setIconSize(12)
        elif self.geomType == "line":
            self.rubberBand = QgsRubberBand(self.canvas, _line_geom)
        else:
            self.rubberBand = QgsRubberBand(self.canvas, _poly_geom)
        self.rubberBand.setColor(Qt.GlobalColor.darkGreen)
        self.rubberBand.setFillColor(QColor(0, 180, 0, 40))
        self.rubberBand.setWidth(2)

        icon_type = QgsRubberBand.IconType.ICON_FULL_DIAMOND
        self.vertexBand = QgsRubberBand(self.canvas, _point_geom)
        self.vertexBand.setIcon(icon_type)
        self.vertexBand.setColor(Qt.GlobalColor.darkGreen)
        self.vertexBand.setIconSize(10)

        box_icon = QgsRubberBand.IconType.ICON_FULL_BOX
        self.highlightBand = QgsRubberBand(self.canvas, _point_geom)
        self.highlightBand.setIcon(box_icon)
        self.highlightBand.setColor(Qt.GlobalColor.red)
        self.highlightBand.setIconSize(12)
        self.highlightBand.hide()
        self._highlightedIndex = -1
        self._extraSnapParts = []

        self._moveTimer = QTimer()
        self._moveTimer.setSingleShot(True)
        self._moveTimer.setInterval(30)
        self._moveTimer.timeout.connect(self._processDeferredMove)
        self._pendingMovePos = None

        self.cursor = QCursor(
            QPixmap(
                [
                    "16 16 3 1",
                    "      c None",
                    ".     c #CC4C2F",
                    "+     c #FFFFFF",
                    "                ",
                    "  ..           ",
                    " .+..          ",
                    " .++..         ",
                    " .+++..        ",
                    "  .++++..      ",
                    "  .+++++..     ",
                    "   .++++++..   ",
                    "   .+++++++..  ",
                    "    .++++++++. ",
                    "    .+++..     ",
                    "     .++.      ",
                    "     .+.       ",
                    "      ..       ",
                    "                ",
                    "                ",
                ]
            )
        )

    def _minPoints(self):
        if self.geomType == "point":
            return 1
        elif self.geomType == "line":
            return 2
        return 3

    @staticmethod
    def _closestPointOnSegment(p, a, b):
        dx, dy = b.x() - a.x(), b.y() - a.y()
        length_sq = dx * dx + dy * dy
        if length_sq == 0:
            return a
        t = ((p.x() - a.x()) * dx + (p.y() - a.y()) * dy) / length_sq
        t = max(0.0, min(1.0, t))
        return QgsPointXY(a.x() + t * dx, a.y() + t * dy)

    def _snapPoint(self, mapPoint, skipSnap=False):
        if skipSnap:
            return mapPoint

        bestDist = float("inf")
        bestPoint = None
        pixelTolerance = 8
        mapTolerance = pixelTolerance * self.canvas.mapUnitsPerPixel()

        # Check extra snap parts for vertex and edge snapping
        for part_pts in self._extraSnapParts:
            for i, pt in enumerate(part_pts):
                d = mapPoint.distance(pt)
                if d < mapTolerance and d < bestDist:
                    bestDist = d
                    bestPoint = pt
            if len(part_pts) >= 2:
                for i in range(len(part_pts) - 1):
                    closest = self._closestPointOnSegment(
                        mapPoint, part_pts[i], part_pts[i + 1]
                    )
                    d = mapPoint.distance(closest)
                    if d < mapTolerance and d < bestDist:
                        bestDist = d
                        bestPoint = closest

        snapUtils = self.canvas.snappingUtils()
        if snapUtils:
            try:
                result = snapUtils.snapToMap(
                    mapPoint, None, QgsPointLocator.Type.Vertex | QgsPointLocator.Type.Edge
                )
                if result.isValid():
                    d = mapPoint.distance(result.point())
                    if d < bestDist:
                        return result.point()
            except (TypeError, RuntimeError):
                pass

        if bestPoint is not None:
            return bestPoint

        return self._manualSnap(mapPoint)

    def _manualSnap(self, mapPoint):
        pixelTolerance = 8
        mapTolerance = pixelTolerance * self.canvas.mapUnitsPerPixel()
        bestDist = mapTolerance
        bestPoint = None
        rect = QgsRectangle(
            mapPoint.x() - mapTolerance,
            mapPoint.y() - mapTolerance,
            mapPoint.x() + mapTolerance,
            mapPoint.y() + mapTolerance,
        )
        for layer in self.canvas.layers():
            if not isinstance(layer, QgsVectorLayer):
                continue
            if not layer.isSpatial():
                continue
            request = QgsFeatureRequest()
            request.setFilterRect(rect)
            for feat in layer.getFeatures(request):
                geom = feat.geometry()
                for v in geom.vertices():
                    pt = QgsPointXY(v.x(), v.y())
                    dist = mapPoint.distance(pt)
                    if dist < bestDist:
                        bestDist = dist
                        bestPoint = pt
        return bestPoint if bestPoint else mapPoint

    def canvasPressEvent(self, e):
        if e.button() == Qt.MouseButton.MiddleButton:
            self._startPan()
            return
        if e.button() == Qt.MouseButton.LeftButton:
            if not self.isDrawing and len(self.points) > 0:
                return
            point = self.toMapCoordinates(e.pos())
            skipSnap = bool(e.modifiers() & Qt.KeyboardModifier.ShiftModifier)
            snapped = self._snapPoint(point, skipSnap)
            self.points.append(snapped)
            self.isDrawing = True
            self.updateRubberBand()
            self.pointAdded.emit(snapped)

    def canvasReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.MiddleButton:
            self._endPan()
            return

    def _startPan(self):
        self._panTool = QgsMapToolPan(self.canvas)
        self._panTool.panningFinished.connect(self._endPan)
        self.canvas.setMapTool(self._panTool)

    def _endPan(self):
        if self._panTool is not None:
            try:
                self._panTool.panningFinished.disconnect(self._endPan)
            except TypeError:
                pass
            self._panTool = None
        self.canvas.setMapTool(self)

    def canvasDoubleClickEvent(self, e):
        if len(self.points) >= self._minPoints():
            self.endDrawing()

    def canvasMoveEvent(self, e):
        if self.geomType == "point":
            return
        if self.isDrawing and len(self.points) > 0:
            pos = self.toMapCoordinates(e.pos())
            skipSnap = bool(e.modifiers() & Qt.KeyboardModifier.ShiftModifier)
            snapped = self._snapPoint(pos, skipSnap)
            self.rubberBand.movePoint(snapped)
            self._pendingMovePos = snapped
            if not self._moveTimer.isActive():
                self._moveTimer.start()

    def _processDeferredMove(self):
        if self._pendingMovePos is not None:
            self.mouseMoved.emit(self._pendingMovePos)
            self._pendingMovePos = None

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Escape:
            self.cancelDrawing()
        elif e.key() == Qt.Key.Key_Return or e.key() == Qt.Key.Key_Enter:
            if len(self.points) >= self._minPoints():
                self.endDrawing()
        elif e.key() == Qt.Key.Key_Backspace or e.key() == Qt.Key.Key_Delete:
            self.undoLastPoint()

    def setHighlightedVertex(self, index):
        self._highlightedIndex = index
        if self.geomType == "point":
            self.highlightBand.hide()
            self.canvas.refresh()
            return
        if 0 <= index < len(self.points):
            self.highlightBand.reset(self._point_geom)
            self.highlightBand.addPoint(self.points[index])
            self.highlightBand.show()
        else:
            self.highlightBand.hide()
        self.canvas.refresh()

    def clearHighlightedVertex(self):
        self._highlightedIndex = -1
        self.highlightBand.hide()
        self.canvas.refresh()

    def updateRubberBand(self):
        if self.geomType == "point":
            self.rubberBand.reset(self._point_geom)
            self.vertexBand.reset(self._point_geom)
            self.highlightBand.reset(self._point_geom)
            self.highlightBand.hide()
            self._highlightedIndex = -1
            if self.points:
                self.rubberBand.addPoint(self.points[-1], True)
                self.rubberBand.show()
            else:
                self.rubberBand.hide()
            self.canvas.refresh()
            return
        elif self.geomType == "line":
            self.rubberBand.reset(self._line_geom)
            self.vertexBand.reset(self._point_geom)
            if not self.points:
                self.rubberBand.hide()
                self.vertexBand.hide()
                self.highlightBand.hide()
                self.canvas.refresh()
                return
            for pt in self.points:
                self.rubberBand.addPoint(pt, False)
            self.rubberBand.addPoint(self.points[-1], False)
            self.rubberBand.movePoint(self.points[-1])
            self.rubberBand.show()
            self.vertexBand.show()
        else:
            self.rubberBand.reset(self._poly_geom)
            self.vertexBand.reset(self._point_geom)
            if not self.points:
                self.rubberBand.hide()
                self.vertexBand.hide()
                self.highlightBand.hide()
                self.canvas.refresh()
                return
            for pt in self.points:
                self.rubberBand.addPoint(pt, False)
            self.rubberBand.addPoint(self.points[-1], False)
            self.rubberBand.movePoint(self.points[-1])
            if len(self.points) > 2:
                self.rubberBand.closePoints(True)
            self.rubberBand.show()
            self.vertexBand.show()

        if 0 <= self._highlightedIndex < len(self.points):
            self.highlightBand.reset(self._point_geom)
            self.highlightBand.addPoint(self.points[self._highlightedIndex])
            self.highlightBand.show()
        else:
            self.highlightBand.hide()

        self.canvas.refresh()

    def finishDrawing(self):
        if len(self.points) >= self._minPoints():
            self.isDrawing = False
            self.drawingFinished.emit(list(self.points))

    def endDrawing(self):
        if len(self.points) >= self._minPoints():
            self.isDrawing = False
            self._drawingEnded = True
            self.updateRubberBand()
            self.drawingEnded.emit()

    def updatePoint(self, index, point):
        if 0 <= index < len(self.points):
            self.points[index] = point
            self.updateRubberBand()

    def undoLastPoint(self):
        if len(self.points) > 0:
            self.points.pop()
            if len(self.points) == 0:
                self.resetRubberBand()
            else:
                self.updateRubberBand()
            if self._drawingEnded:
                self._drawingEnded = False
                self.isDrawing = True

    def cancelDrawing(self):
        self.isDrawing = False
        self.points.clear()
        self.resetRubberBand()
        self.canceled.emit()

    def resetRubberBand(self):
        if self.geomType == "point":
            self.rubberBand.reset(self._point_geom)
        elif self.geomType == "line":
            self.rubberBand.reset(self._line_geom)
        else:
            self.rubberBand.reset(self._poly_geom)
        self.vertexBand.reset(self._point_geom)
        self.highlightBand.reset(self._point_geom)
        self.rubberBand.hide()
        self.vertexBand.hide()
        self.highlightBand.hide()
        self._highlightedIndex = -1
        self.canvas.refresh()

    def clear(self):
        self.points.clear()
        self.isDrawing = False
        self._drawingEnded = False
        self._highlightedIndex = -1
        self.resetRubberBand()

    def activate(self):
        self.canvas.setCursor(self.cursor)
        self._enableSnapping()
        super().activate()

    def deactivate(self):
        self.clear()
        self._restoreSnapping()
        super().deactivate()

    def _enableSnapping(self):
        proj = QgsProject.instance()
        self._origSnapConfig = proj.snappingConfig()
        cfg = QgsSnappingConfig(self._origSnapConfig)
        cfg.setMode(QgsSnappingConfig.SnappingMode.AllLayers)
        cfg.setTolerance(8)
        cfg.setUnits(QgsTolerance.UnitType.Pixels)
        if hasattr(cfg, "setSnapType"):
            cfg.setSnapType(QgsSnappingConfig.SnappingType.VertexAndSegment)
        elif hasattr(cfg, "setType"):
            cfg.setType(QgsSnappingConfig.SnappingType.VertexAndSegment)
        proj.setSnappingConfig(cfg)
        snapUtils = self.canvas.snappingUtils()
        if snapUtils is not None:
            if hasattr(snapUtils, "setConfig"):
                snapUtils.setConfig(cfg)
            elif hasattr(snapUtils, "readConfigFromProject"):
                snapUtils.readConfigFromProject()
            elif hasattr(snapUtils, "readFromProject"):
                snapUtils.readFromProject()

    def _restoreSnapping(self):
        if self._origSnapConfig is not None:
            QgsProject.instance().setSnappingConfig(self._origSnapConfig)
            self._origSnapConfig = None

    def setPoints(self, points):
        self.points = list(points)
        self.updateRubberBand()

    def getPoints(self):
        return list(self.points)

    def setExtraSnapParts(self, parts):
        self._extraSnapParts = [list(p) for p in parts]
