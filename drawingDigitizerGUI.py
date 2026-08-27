# -*- coding: utf-8 -*-


from qgis.PyQt.QtCore import Qt, pyqtSignal, QSize, QTimer
from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QComboBox,
    QToolButton,
    QApplication,
    QListWidget,
    QMessageBox,
    QSizePolicy,
)
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCsException,
    QgsDistanceArea,
    QgsProject,
    QgsPointXY,
    QgsLineString,
    QgsPolygon,
    QgsGeometry,
    QgsCoordinateTransform,
    QgsApplication,
    QgsWkbTypes,
)
from qgis.gui import QgsProjectionSelectionDialog, QgsRubberBand
from qgis.PyQt.QtCore import QSettings

import os

_PLUGIN_DIR = os.path.dirname(__file__)

# ---------------------------------------------------------------------------
# Full stylesheet for DrawingDigitizerGUI
# ---------------------------------------------------------------------------
_DRAW_STYLE = """
QDialog {
    background-color: #f5f6fa;
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 9pt;
}

/* Header banner */
#headerFrame {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #1a5276, stop:1 #2980b9);
    border-radius: 6px;
    padding: 2px;
}
#headerTitle {
    color: white;
    font-size: 12pt;
    font-weight: bold;
}
#headerSub {
    color: #aed6f1;
    font-size: 8pt;
}

/* Group boxes */
QGroupBox {
    font-weight: bold;
    font-size: 9pt;
    color: #2c3e50;
    border: 1px solid #c8d6e5;
    border-radius: 6px;
    margin-top: 8px;
    padding-top: 6px;
    background-color: #ffffff;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    background-color: #f5f6fa;
    color: #2980b9;
}

/* Instruction label */
#instrLabel {
    color: #5d6d7e;
    font-style: italic;
    padding: 4px 6px;
    background: #eaf2fb;
    border-radius: 4px;
    border-left: 3px solid #2980b9;
}

/* Status bar */
#statusFrame {
    background-color: #eaf2fb;
    border: 1px solid #aed6f1;
    border-radius: 4px;
    padding: 2px 6px;
}
#pointCountLabel {
    font-weight: bold;
    color: #1a5276;
    font-size: 9pt;
}

/* Coordinate table */
QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #eaf2fb;
    gridline-color: #d5d8dc;
    border: 1px solid #c8d6e5;
    border-radius: 4px;
    selection-background-color: #2980b9;
    selection-color: white;
    font-size: 9pt;
}
QTableWidget::item { padding: 2px 5px; }
QTableWidget::item:selected { background-color: #2980b9; color: white; }
QHeaderView::section {
    background-color: #2c3e50;
    color: #ecf0f1;
    font-weight: bold;
    font-size: 9pt;
    padding: 4px 5px;
    border: none;
    border-right: 1px solid #3d5166;
}

/* Parts list */
QListWidget {
    background-color: #ffffff;
    border: 1px solid #c8d6e5;
    border-radius: 4px;
    color: #2c3e50;
    font-size: 9pt;
}
QListWidget::item:selected {
    background-color: #2980b9;
    color: white;
    border-radius: 3px;
}
QListWidget::item:hover {
    background-color: #d6eaf8;
}

/* Area frame */
#areaFrame {
    background: #eafaf1;
    border: 1px solid #a9dfbf;
    border-radius: 5px;
    padding: 4px;
}
#areaHaLabel {
    font-weight: bold;
    font-size: 11pt;
    color: #27ae60;
}
#areaTotalLabel {
    font-weight: bold;
    font-size: 11pt;
    color: #1e8449;
}

/* Length frame */
#lengthFrame {
    background: #eaf2fb;
    border: 1px solid #aed6f1;
    border-radius: 5px;
    padding: 4px;
}
#lengthLabel {
    font-weight: bold;
    font-size: 11pt;
    color: #1a5276;
}

/* Action buttons row */
QPushButton#btnUndo {
    background-color: #e67e22;
    color: white; border: none;
    border-radius: 5px; padding: 5px 10px;
    font-weight: bold; font-size: 9pt; min-height: 22px;
}
QPushButton#btnUndo:hover   { background-color: #f39c12; }
QPushButton#btnUndo:pressed { background-color: #ca6f1e; }
QPushButton#btnUndo:disabled { background-color: #bdc3c7; color: #7f8c8d; }

QPushButton#btnEnd {
    background-color: #2980b9;
    color: white; border: none;
    border-radius: 5px; padding: 5px 10px;
    font-weight: bold; font-size: 9pt; min-height: 22px;
}
QPushButton#btnEnd:hover   { background-color: #3498db; }
QPushButton#btnEnd:pressed { background-color: #1a6fa3; }
QPushButton#btnEnd:disabled { background-color: #bdc3c7; color: #7f8c8d; }

QPushButton#btnFinish {
    background-color: #27ae60;
    color: white; border: none;
    border-radius: 5px; padding: 5px 14px;
    font-weight: bold; font-size: 10pt; min-height: 26px;
}
QPushButton#btnFinish:hover   { background-color: #2ecc71; }
QPushButton#btnFinish:pressed { background-color: #1e8449; }
QPushButton#btnFinish:disabled { background-color: #bdc3c7; color: #7f8c8d; }

QPushButton#btnRestart {
    background-color: #ffffff;
    color: #c0392b;
    border: 1px solid #c0392b;
    border-radius: 5px; padding: 4px 10px;
    font-weight: bold; font-size: 9pt;
}
QPushButton#btnRestart:hover {
    background-color: #c0392b; color: white;
}

QPushButton#btnClose {
    background-color: #7f8c8d;
    color: white; border: none;
    border-radius: 5px; padding: 4px 10px;
    font-weight: bold; font-size: 9pt;
}
QPushButton#btnClose:hover { background-color: #95a5a6; }

/* Part tool buttons */
QToolButton#btnAddPart,
QToolButton#btnAddRing,
QToolButton#btnRemovePart,
QToolButton#btnUndoPart {
    background-color: #ffffff;
    border: 1px solid #c8d6e5;
    border-radius: 4px;
    padding: 2px;
    color: #2c3e50;
    font-size: 8pt;
}
QToolButton#btnAddPart:hover,
QToolButton#btnAddRing:hover,
QToolButton#btnRemovePart:hover,
QToolButton#btnUndoPart:hover {
    background-color: #d6eaf8;
    border-color: #2980b9;
}
QToolButton#btnAddPart:pressed,
QToolButton#btnAddRing:pressed,
QToolButton#btnRemovePart:pressed,
QToolButton#btnUndoPart:pressed {
    background-color: #2980b9;
    border-color: #1a6fa3;
}

/* CRS select button */
QPushButton#btnSelectCrs {
    background-color: #2c3e50;
    color: white; border: none;
    border-radius: 4px; padding: 3px 8px; font-size: 9pt;
}
QPushButton#btnSelectCrs:hover { background-color: #3d5166; }

QLabel#crsNameLabel {
    color: #2980b9;
    font-style: italic;
    font-size: 9pt;
}

/* Scroll bars */
QScrollBar:vertical {
    background: #f0f3f4; width: 10px; border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #aab7b8; border-radius: 5px; min-height: 20px;
}
QScrollBar::handle:vertical:hover { background: #7f8c8d; }
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical { height: 0; }
"""


class DrawingDigitizerGUI(QDialog):
    finishedDrawing = pyqtSignal(list)
    coordCrsChanged = pyqtSignal(object)
    restartRequested = pyqtSignal()
    undoRequested = pyqtSignal()
    pointEdited = pyqtSignal(int, object)
    drawingEnded = pyqtSignal()
    vertexSelected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vectorel Digitizer Pro \u2013 Drawing Digitizer")
        self.setModal(False)
        self.resize(420, 540)
        self.setMinimumWidth(380)

        self.featureCrs = None
        self.otherCrs = None
        self.projectCrs = None
        self.parts = [[1, []]]
        self._currentPartIndex = 0
        self.__contursCount = 1
        self.__ringsCount = 0
        self.__deletedPart = None
        self._previewPt = None
        self._drawingEnded = False
        self.mapCanvas = None
        self.drawTool = None
        self.geomType = "polygon"

        self._cachedTransformForward = None
        self._cachedTransformReverse = None
        self._cachedTransformProjectCrs = None
        self._cachedTransformFeatureCrs = None

        self._completedBands = {}

        self._areaTimer = QTimer()
        self._areaTimer.setSingleShot(True)
        self._areaTimer.setInterval(50)
        self._areaTimer.timeout.connect(self._doDeferredAreaUpdate)
        self._pendingAreaPreview = False

        self._setupUi()
        self._connectSignals()
        self.setStyleSheet(_DRAW_STYLE)
        self._updatePartList()

    @property
    def _currentPoints(self):
        if 0 <= self._currentPartIndex < len(self.parts):
            return self.parts[self._currentPartIndex][1]
        return []

    def _setCurrentPoints(self, value):
        if 0 <= self._currentPartIndex < len(self.parts):
            self.parts[self._currentPartIndex][1] = value

    # ------------------------------------------------------------------
    def _setupUi(self):
        root = QVBoxLayout(self)
        root.setSpacing(7)
        root.setContentsMargins(8, 8, 8, 8)

        # -- Header banner -------------------------------------------------
        hdrFrame = QFrame()
        hdrFrame.setObjectName("headerFrame")
        hdrLayout = QVBoxLayout(hdrFrame)
        hdrLayout.setContentsMargins(10, 6, 10, 6)
        hdrLayout.setSpacing(1)

        titleLbl = QLabel("Drawing Digitizer")
        titleLbl.setObjectName("headerTitle")
        subLbl = QLabel("Click the map to add polygon vertices")
        subLbl.setObjectName("headerSub")
        hdrLayout.addWidget(titleLbl)
        hdrLayout.addWidget(subLbl)
        root.addWidget(hdrFrame)

        # -- CRS group -----------------------------------------------------
        crsGroup = QGroupBox("CRS Selection")
        crsLayout = QVBoxLayout(crsGroup)
        crsLayout.setContentsMargins(8, 8, 8, 8)
        crsLayout.setSpacing(4)

        crsRow = QHBoxLayout()
        self.lblCrsInfo = QLabel("CRS not selected")
        self.lblCrsInfo.setMinimumHeight(24)
        crsRow.addWidget(self.lblCrsInfo, 1)
        self.tbSelectCrs = QToolButton()
        self.tbSelectCrs.setMinimumSize(28, 28)
        self.tbSelectCrs.setMaximumSize(28, 28)
        self.tbSelectCrs.setIcon(
            QgsApplication.getThemeIcon("mIconProjectionEnabled.svg")
        )
        self.tbSelectCrs.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.tbSelectCrs.setIconSize(QSize(20, 20))
        self.tbSelectCrs.setToolTip("Select CRS")
        crsRow.addWidget(self.tbSelectCrs)
        crsLayout.addLayout(crsRow)
        root.addWidget(crsGroup)

        # -- Instruction ---------------------------------------------------
        self._instrLbl = QLabel(
            "Left-click to add vertices  \u00b7  "
            "Double-click or press Enter to finish  \u00b7  "
            "Esc to cancel\n"
            "Hold Shift to temporarily disable snap"
        )
        self._instrLbl.setObjectName("instrLabel")
        self._instrLbl.setWordWrap(True)
        root.addWidget(self._instrLbl)

        # -- Status bar ----------------------------------------------------
        statusFrame = QFrame()
        statusFrame.setObjectName("statusFrame")
        statusRow = QHBoxLayout(statusFrame)
        statusRow.setContentsMargins(4, 2, 4, 2)
        self.lblPointCount = QLabel("Vertices: 0")
        self.lblPointCount.setObjectName("pointCountLabel")
        statusRow.addWidget(self.lblPointCount)
        statusRow.addStretch()
        root.addWidget(statusFrame)

        # -- Table toolbar (Copy/Paste/AddRow/DelRow) ----------------------
        tblToolbar = QFrame()
        tblToolbar.setObjectName("tblToolbar")
        tblToolbar.setStyleSheet("QFrame#tblToolbar { background: transparent; }")
        tbLayout = QHBoxLayout(tblToolbar)
        tbLayout.setContentsMargins(0, 0, 0, 0)
        tbLayout.setSpacing(2)

        _img_dir = os.path.join(_PLUGIN_DIR, "images")

        def _iconFile(name):
            p = os.path.join(_img_dir, name)
            if os.path.isfile(p):
                return QIcon(p)
            return QIcon()

        self.toolButtonCopy = QToolButton()
        self.toolButtonCopy.setMinimumSize(QSize(32, 32))
        self.toolButtonCopy.setMaximumSize(QSize(32, 32))
        self.toolButtonCopy.setIcon(_iconFile("mActionEditCopy.svg"))
        self.toolButtonCopy.setIconSize(QSize(24, 24))
        self.toolButtonCopy.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.toolButtonCopy.setToolTip("Copy coordinates to clipboard")

        self.toolButtonPaste = QToolButton()
        self.toolButtonPaste.setMinimumSize(QSize(32, 32))
        self.toolButtonPaste.setMaximumSize(QSize(32, 32))
        self.toolButtonPaste.setIcon(_iconFile("mActionEditPaste.svg"))
        self.toolButtonPaste.setIconSize(QSize(24, 24))
        self.toolButtonPaste.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.toolButtonPaste.setToolTip("Paste coordinates from clipboard")

        self.toolButtonSwap = QToolButton()
        self.toolButtonSwap.setMinimumSize(QSize(32, 32))
        self.toolButtonSwap.setMaximumSize(QSize(32, 32))
        self.toolButtonSwap.setIcon(_iconFile("swap.svg"))
        self.toolButtonSwap.setIconSize(QSize(24, 24))
        self.toolButtonSwap.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.toolButtonSwap.setToolTip("Swap X and Y columns")

        self.toolButtonAddRows = QToolButton()
        self.toolButtonAddRows.setMinimumSize(QSize(32, 32))
        self.toolButtonAddRows.setMaximumSize(QSize(32, 32))
        self.toolButtonAddRows.setIcon(_iconFile("mActionNewTableRow.svg"))
        self.toolButtonAddRows.setIconSize(QSize(24, 24))
        self.toolButtonAddRows.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.toolButtonAddRows.setToolTip("Add row")

        self.toolButtonRemoveRows = QToolButton()
        self.toolButtonRemoveRows.setMinimumSize(QSize(32, 32))
        self.toolButtonRemoveRows.setMaximumSize(QSize(32, 32))
        self.toolButtonRemoveRows.setIcon(_iconFile("mActionDeleteTableRow.svg"))
        self.toolButtonRemoveRows.setIconSize(QSize(24, 24))
        self.toolButtonRemoveRows.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonIconOnly
        )
        self.toolButtonRemoveRows.setToolTip("Delete selected rows")

        tbLayout.addWidget(self.toolButtonCopy)
        tbLayout.addWidget(self.toolButtonPaste)
        tbLayout.addWidget(self.toolButtonSwap)
        tbLayout.addWidget(self.toolButtonAddRows)
        tbLayout.addWidget(self.toolButtonRemoveRows)
        tbLayout.addStretch()

        # -- Part buttons (Add Part / Add Ring / Remove Part / Undo Remove)
        self.btnAddPart = QToolButton()
        self.btnAddPart.setObjectName("btnAddPart")
        self.btnAddPart.setMinimumSize(QSize(32, 32))
        self.btnAddPart.setMaximumSize(QSize(32, 32))
        self.btnAddPart.setIcon(_iconFile("mActionAddPart.svg"))
        self.btnAddPart.setIconSize(QSize(24, 24))
        self.btnAddPart.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.btnAddPart.setToolTip("Add a new exterior part")

        self.btnAddRing = QToolButton()
        self.btnAddRing.setObjectName("btnAddRing")
        self.btnAddRing.setMinimumSize(QSize(32, 32))
        self.btnAddRing.setMaximumSize(QSize(32, 32))
        self.btnAddRing.setIcon(_iconFile("mActionAddRing.svg"))
        self.btnAddRing.setIconSize(QSize(24, 24))
        self.btnAddRing.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.btnAddRing.setToolTip("Add a ring (hole) to the current part")

        self.btnRemovePart = QToolButton()
        self.btnRemovePart.setObjectName("btnRemovePart")
        self.btnRemovePart.setMinimumSize(QSize(32, 32))
        self.btnRemovePart.setMaximumSize(QSize(32, 32))
        self.btnRemovePart.setIcon(_iconFile("mActionDeletePart.svg"))
        self.btnRemovePart.setIconSize(QSize(24, 24))
        self.btnRemovePart.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.btnRemovePart.setToolTip("Remove the selected part")

        self.btnUndoPart = QToolButton()
        self.btnUndoPart.setObjectName("btnUndoPart")
        self.btnUndoPart.setMinimumSize(QSize(32, 32))
        self.btnUndoPart.setMaximumSize(QSize(32, 32))
        self.btnUndoPart.setIcon(
            QgsApplication.getThemeIcon("mActionUndo.svg")
        )
        self.btnUndoPart.setIconSize(QSize(24, 24))
        self.btnUndoPart.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.btnUndoPart.setToolTip("Undo last part removal")
        self.btnUndoPart.setEnabled(False)

        tbLayout.addWidget(self.btnAddPart)
        tbLayout.addWidget(self.btnAddRing)
        tbLayout.addWidget(self.btnRemovePart)
        tbLayout.addWidget(self.btnUndoPart)
        root.addWidget(tblToolbar)

        # -- Table + Parts list side by side --------------------------------
        tableArea = QHBoxLayout()
        tableArea.setSpacing(6)

        # -- Parts list ----------------------------------------------------
        partsFrame = QFrame()
        partsLayout = QVBoxLayout(partsFrame)
        partsLayout.setContentsMargins(0, 0, 0, 0)
        partsLayout.setSpacing(3)

        lblParts = QLabel("Parts")
        lblParts.setStyleSheet(
            "font-weight: bold; font-size: 9pt; color: #2c3e50;"
        )
        partsLayout.addWidget(lblParts)

        self.listParts = QListWidget()
        self.listParts.setMinimumWidth(70)
        self.listParts.setMaximumWidth(90)
        self.listParts.setMinimumHeight(90)
        self.listParts.setMaximumHeight(160)
        policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.listParts.setSizePolicy(policy)
        partsLayout.addWidget(self.listParts)

        tableArea.addWidget(partsFrame)

        # -- Coordinate table ----------------------------------------------
        self.tblCoords = QTableWidget(0, 3)
        self.tblCoords.setHorizontalHeaderLabels(["#", "X", "Y"])
        self.tblCoords.setMaximumHeight(160)
        self.tblCoords.setMinimumHeight(90)
        self.tblCoords.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.tblCoords.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tblCoords.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.tblCoords.verticalHeader().hide()
        self.tblCoords.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.tblCoords.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        self.tblCoords.setAlternatingRowColors(True)
        f = self.tblCoords.font()
        f.setPointSize(9)
        self.tblCoords.setFont(f)
        tableArea.addWidget(self.tblCoords, 1)

        root.addLayout(tableArea)

        # -- Area display --------------------------------------------------
        self._area_sqm = 0.0
        self._area_total_sqm = 0.0

        self.areaFrame = QFrame()
        self.areaFrame.setObjectName("areaFrame")
        areaLayout = QVBoxLayout(self.areaFrame)
        areaLayout.setContentsMargins(8, 6, 8, 6)
        areaLayout.setSpacing(1)

        lblTitle = QLabel("Calculated Area")
        lblTitle.setStyleSheet("font-weight: bold; font-size: 11pt; color: #1a5c32;")
        areaLayout.addWidget(lblTitle)

        unitRow = QHBoxLayout()
        unitRow.setSpacing(4)
        lblUnit = QLabel("Unit:")
        lblUnit.setStyleSheet("font-size: 9pt; color: #27ae60;")
        self.cbAreaUnit = QComboBox()
        self.cbAreaUnit.addItems(
            [
                "Hectares",
                "Acres",
                "Square Feet",
                "Square Meters",
                "Square Kilometers",
                "Square Miles",
            ]
        )
        self.cbAreaUnit.setStyleSheet("font-size: 9pt; color: #27ae60;")
        self.cbAreaUnit.currentIndexChanged.connect(self._onAreaUnitChanged)
        unitRow.addWidget(lblUnit)
        unitRow.addWidget(self.cbAreaUnit, 1)
        areaLayout.addLayout(unitRow)

        self.lblArea = QLabel("Area: \u2014")
        self.lblArea.setObjectName("areaHaLabel")
        areaLayout.addWidget(self.lblArea)

        self.areaSeparator = QFrame()
        self.areaSeparator.setFrameShape(QFrame.Shape.HLine)
        self.areaSeparator.setFrameShadow(QFrame.Shadow.Sunken)
        self.areaSeparator.hide()
        areaLayout.addWidget(self.areaSeparator)

        self.lblTotalArea = QLabel("Total: \u2014")
        self.lblTotalArea.setObjectName("areaTotalLabel")
        self.lblTotalArea.hide()
        areaLayout.addWidget(self.lblTotalArea)

        self.areaFrame.hide()
        root.addWidget(self.areaFrame)

        # -- Length display -------------------------------------------------
        self._length_m = 0.0

        self.lengthFrame = QFrame()
        self.lengthFrame.setObjectName("lengthFrame")
        lengthLayout = QVBoxLayout(self.lengthFrame)
        lengthLayout.setContentsMargins(8, 6, 8, 6)
        lengthLayout.setSpacing(1)

        lblLenTitle = QLabel("Calculated Length")
        lblLenTitle.setStyleSheet("font-weight: bold; font-size: 11pt; color: #1a5276;")
        lengthLayout.addWidget(lblLenTitle)

        lenUnitRow = QHBoxLayout()
        lenUnitRow.setSpacing(4)
        lblLenUnit = QLabel("Unit:")
        lblLenUnit.setStyleSheet("font-size: 9pt; color: #2980b9;")
        self.cbLengthUnit = QComboBox()
        self.cbLengthUnit.addItems(["Meters", "Kilometers", "Feet", "Miles", "Yards"])
        self.cbLengthUnit.setStyleSheet("font-size: 9pt; color: #2980b9;")
        self.cbLengthUnit.currentIndexChanged.connect(self._onLengthUnitChanged)
        lenUnitRow.addWidget(lblLenUnit)
        lenUnitRow.addWidget(self.cbLengthUnit, 1)
        lengthLayout.addLayout(lenUnitRow)

        self.lblLength = QLabel("Length: \u2014")
        self.lblLength.setObjectName("lengthLabel")
        lengthLayout.addWidget(self.lblLength)
        self.lengthFrame.hide()
        root.addWidget(self.lengthFrame)

        root.addStretch()

        # -- Action buttons ------------------------------------------------
        actionRow = QHBoxLayout()
        actionRow.setSpacing(6)

        self.btnUndo = QPushButton("\u21a9  Undo")
        self.btnUndo.setObjectName("btnUndo")
        self.btnUndo.setToolTip("Remove last vertex (Backspace)")

        self.btnEnd = QPushButton("\u23f9  End Drawing")
        self.btnEnd.setObjectName("btnEnd")
        self.btnEnd.setToolTip("Close polygon without finishing the dialog")

        self.btnFinish = QPushButton("\u2714  Save Feature")
        self.btnFinish.setObjectName("btnFinish")
        self.btnFinish.setToolTip("Save as a new layer feature (Enter)")

        actionRow.addWidget(self.btnUndo)
        actionRow.addWidget(self.btnEnd)
        actionRow.addWidget(self.btnFinish, 1)
        root.addLayout(actionRow)

        # -- Bottom buttons ------------------------------------------------
        bottomRow = QHBoxLayout()
        bottomRow.setSpacing(6)

        self.btnRestart = QPushButton("\U0001f504  Restart")
        self.btnRestart.setObjectName("btnRestart")
        self.btnRestart.setToolTip("Clear all points and start over")

        self.btnClose = QPushButton("\u2715  Close")
        self.btnClose.setObjectName("btnClose")
        self.btnClose.setToolTip("Close dialog and discard current drawing")

        bottomRow.addWidget(self.btnRestart)
        bottomRow.addStretch()
        bottomRow.addWidget(self.btnClose)
        root.addLayout(bottomRow)

    # ------------------------------------------------------------------
    def _connectSignals(self):
        self.tbSelectCrs.clicked.connect(self._selectCustomCrs)

        self.tblCoords.cellChanged.connect(self._onCellEdited)
        self.tblCoords.cellClicked.connect(self._onCellClicked)

        self.toolButtonCopy.clicked.connect(self._copyCoords)
        self.toolButtonPaste.clicked.connect(self._pasteCoords)
        self.toolButtonSwap.clicked.connect(self._swapXY)
        self.toolButtonAddRows.clicked.connect(self._addRow)
        self.toolButtonRemoveRows.clicked.connect(self._deleteRow)

        self.btnUndo.clicked.connect(self.undoPoint)
        self.btnEnd.clicked.connect(self._onEndDrawing)
        self.btnFinish.clicked.connect(self.finishDrawing)
        self.btnRestart.clicked.connect(self.restartDrawing)
        self.btnClose.clicked.connect(self.reject)

        self.btnAddPart.clicked.connect(self._addPart)
        self.btnAddRing.clicked.connect(self._addRing)
        self.btnRemovePart.clicked.connect(self._removePart)
        self.btnUndoPart.clicked.connect(self._undoPart)
        self.listParts.currentRowChanged.connect(self._onPartSelected)

    # ------------------------------------------------------------------
    def setCanvas(self, canvas):
        self.mapCanvas = canvas
        self.projectCrs = canvas.mapSettings().destinationCrs()

        dlg = QgsProjectionSelectionDialog()
        layer_crs = canvas.currentLayer().crs()
        if layer_crs.isValid():
            dlg.setCrs(layer_crs)
        saved_wkt = QSettings().value(
            "/Plugin-VectorelDigitizerPro/LastCrsWkt", "", type=str
        )
        if saved_wkt:
            crs = QgsCoordinateReferenceSystem.fromWkt(saved_wkt)
            if crs.isValid():
                dlg.setCrs(crs)
        if dlg.exec():
            self.featureCrs = dlg.crs()
        elif layer_crs.isValid():
            self.featureCrs = layer_crs
        self._invalidateTransformCache()
        self.lblCrsInfo.setText(self._crsDisplayText(self.featureCrs))
        self.coordCrsChanged.emit(self.featureCrs)

    # ------------------------------------------------------------------
    def setGeometryType(self, geomType):
        self.geomType = geomType
        if geomType == "point":
            self._instrLbl.setText(
                "Left-click on the map to place a point  \u00b7  "
                "Click again to reposition  \u00b7  "
                "Save Feature to confirm\n"
                "Hold Shift to temporarily disable snap"
            )
            self.areaFrame.hide()
            self.lengthFrame.hide()
            self.btnEnd.setEnabled(False)
            self.btnEnd.setToolTip("Not available for point geometry")
            self.btnUndo.setEnabled(True)
        elif geomType == "line":
            self._instrLbl.setText(
                "Left-click to add vertices  \u00b7  "
                "Double-click or press Enter to finish  \u00b7  "
                "Esc to cancel\n"
                "Hold Shift to temporarily disable snap"
            )
            self.areaFrame.hide()
            self.lengthFrame.show()
            self.btnEnd.setEnabled(True)
            self.btnEnd.setToolTip("Finish line without closing")
            self.btnUndo.setEnabled(True)
        else:
            self._instrLbl.setText(
                "Left-click to add vertices  \u00b7  "
                "Double-click or press Enter to finish  \u00b7  "
                "Esc to cancel\n"
                "Hold Shift to temporarily disable snap"
            )
            self.areaFrame.show()
            self.lengthFrame.hide()
            self.btnEnd.setEnabled(True)
            self.btnEnd.setToolTip("Close polygon without finishing the dialog")
            self.btnUndo.setEnabled(True)

    # ------------------------------------------------------------------
    def _minPoints(self):
        if self.geomType == "point":
            return 1
        elif self.geomType == "line":
            return 2
        return 3

    # ------------------------------------------------------------------
    # CRS selection
    # ------------------------------------------------------------------
    def _crsDisplayText(self, crs):
        desc = crs.description()
        auth = crs.authid()
        if desc:
            return f"{desc} ({auth})"
        return auth

    def _selectCustomCrs(self):
        dlg = QgsProjectionSelectionDialog()
        dlg.setCrs(
            self.featureCrs
            if (self.featureCrs and self.featureCrs.isValid())
            else QgsCoordinateReferenceSystem("EPSG:4326")
        )
        if dlg.exec():
            new_crs = dlg.crs()
            if not new_crs.isValid():
                return
            old = self.featureCrs
            self.featureCrs = new_crs
            self._invalidateTransformCache()
            self.lblCrsInfo.setText(self._crsDisplayText(new_crs))
            self.coordCrsChanged.emit(new_crs)
            if old is not None and old.isValid() and old != new_crs:
                self._updateCoordList()
                self._updateArea()
                self._updateLength()

    # ------------------------------------------------------------------
    # Point management
    # ------------------------------------------------------------------
    def addPoint(self, point):
        pts = self._currentPoints
        if self.geomType == "point":
            pts.clear()
            pts.append(point)
        else:
            pts.append(point)
        self.lblPointCount.setText("Vertices: %d" % len(pts))
        self._updateCoordList(incremental=True)
        self._updateArea()
        self._updateLength()
        self.vertexSelected.emit(len(pts) - 1)

    def undoPoint(self):
        pts = self._currentPoints
        if pts:
            if self.geomType == "point":
                pts.clear()
            else:
                pts.pop()
            self.lblPointCount.setText("Vertices: %d" % len(pts))
            self._updateCoordList()
            self._updateArea()
            self._updateLength()
            self.undoRequested.emit()
            if pts:
                self.vertexSelected.emit(len(pts) - 1)
            if self._drawingEnded:
                self._drawingEnded = False
                if pts:
                    self.setPreviewPoint(pts[-1])

    def sortCoordinatesClockwise(self):
        pts = self._currentPoints
        if len(pts) < 3:
            return

        pts_fmt = []
        for pt in pts:
            x, y = self._formatCoords(pt)
            pts_fmt.append((x, y))

        xs = [p[0] for p in pts_fmt]
        ys = [p[1] for p in pts_fmt]
        min_x = min(xs)
        max_y = max(ys)

        nw_idx = 0
        nw_dist = float("inf")
        for i, (x, y) in enumerate(pts_fmt):
            d = (x - min_x) ** 2 + (max_y - y) ** 2
            if d < nw_dist:
                nw_dist = d
                nw_idx = i

        area = 0.0
        n = len(pts_fmt)
        for i in range(n):
            j = (i + 1) % n
            area += pts_fmt[i][0] * pts_fmt[j][1]
            area -= pts_fmt[j][0] * pts_fmt[i][1]

        reordered = []
        for i in range(n):
            idx = (nw_idx + i) % n
            reordered.append(pts[idx])

        if area > 0:
            reordered = [reordered[0]] + reordered[1:][::-1]

        self._setCurrentPoints(reordered)
        self._updateCoordList()
        self._updateArea()
        self.vertexSelected.emit(0)
        self.lblPointCount.setText(
            "Vertices: %d (sorted CW from NW)" % len(self._currentPoints)
        )

    # ------------------------------------------------------------------
    # Part management
    # ------------------------------------------------------------------
    def _updatePartList(self):
        self.listParts.blockSignals(True)
        self.listParts.clear()
        for part_num, _ in self.parts:
            self.listParts.addItem(str(part_num))
        self.listParts.blockSignals(False)
        if 0 <= self._currentPartIndex < self.listParts.count():
            self.listParts.setCurrentRow(self._currentPartIndex)
        elif self.listParts.count() > 0:
            self.listParts.setCurrentRow(0)
            self._currentPartIndex = 0

    def _onPartSelected(self, idx):
        if idx < 0 or idx >= len(self.parts) or idx == self._currentPartIndex:
            return
        self._commitCurrentPartToTool()
        self._currentPartIndex = idx
        self._loadPartFromTool()
        self.lblPointCount.setText(
            "Vertices: %d" % len(self._currentPoints)
        )
        self._updateCoordList()
        self._updateArea()
        self._updateLength()

    def _updateSnapPoints(self):
        if self.drawTool is None:
            return
        snap_parts = []
        for i, (_, pts) in enumerate(self.parts):
            if i != self._currentPartIndex and pts:
                snap_parts.append(pts)
        self.drawTool.setExtraSnapParts(snap_parts)

    def _commitCurrentPartToTool(self):
        if self.drawTool is not None:
            pts = list(self.drawTool.getPoints())
            self._setCurrentPoints(pts)
            self._saveCompletedBand(self._currentPartIndex, pts)
            self._updateSnapPoints()

    def _loadPartFromTool(self):
        if self.drawTool is not None:
            pts = list(self._currentPoints)
            self._removeCompletedBand(self._currentPartIndex)
            self.drawTool.setPoints(pts)
            self.drawTool.isDrawing = len(pts) > 0
            self._drawingEnded = False
            self._updateSnapPoints()

    def _getRubberBandGeomType(self):
        if self.geomType == "polygon":
            return QgsWkbTypes.GeometryType.PolygonGeometry
        return QgsWkbTypes.GeometryType.LineGeometry

    def _saveCompletedBand(self, part_idx, pts):
        self._removeCompletedBand(part_idx)
        if not pts or self.geomType == "point":
            return
        if not self.mapCanvas:
            return
        band = QgsRubberBand(self.mapCanvas, self._getRubberBandGeomType())
        band.setColor(Qt.GlobalColor.darkGreen)
        band.setWidth(2)
        if self.geomType == "polygon":
            band.setFillColor(QColor(0, 180, 0, 40))
        for pt in pts:
            band.addPoint(pt)
        if self.geomType == "polygon":
            band.closePoints(True)
        band.show()
        self._completedBands[part_idx] = band

    def _removeCompletedBand(self, part_idx):
        if part_idx in self._completedBands:
            band = self._completedBands.pop(part_idx)
            band.reset()
            band.hide()

    def _addPart(self):
        self.__contursCount += 1
        self.parts.append([self.__contursCount, []])
        self._updatePartList()
        self.listParts.setCurrentRow(len(self.parts) - 1)
        self._onPartSelected(len(self.parts) - 1)
        self._updateArea()

    def _addRing(self):
        self.__ringsCount += 1
        current_row = self._currentPartIndex
        insert_pos = current_row + 1
        self.parts.insert(insert_pos, [-self.__ringsCount, []])
        self._updatePartList()
        self.listParts.setCurrentRow(insert_pos)
        self._updateArea()

    def _removePart(self):
        if self._currentPartIndex < 0 or self._currentPartIndex >= len(self.parts):
            return
        reply = QMessageBox.question(
            self,
            "Confirm delete",
            "Are you sure to delete this part?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self._commitCurrentPartToTool()

        deleted_data = self.parts[self._currentPartIndex]
        part_number = deleted_data[0]
        self.__deletedPart = {
            "row": self._currentPartIndex,
            "number": part_number,
            "part": [part_number, list(deleted_data[1])],
        }
        self.btnUndoPart.setEnabled(True)

        self._removeCompletedBand(self._currentPartIndex)
        self.parts.pop(self._currentPartIndex)

        if part_number > 0:
            self.__contursCount -= 1
        else:
            self.__ringsCount -= 1

        if len(self.parts) == 0:
            self.__contursCount = 0
            self.__ringsCount = 0

        new_idx = min(self._currentPartIndex, max(0, len(self.parts) - 1))
        self._currentPartIndex = new_idx
        self._updatePartList()
        self._loadPartFromTool()
        if self.drawTool is not None and self._currentPoints:
            self.drawTool.isDrawing = False
            self.drawTool._drawingEnded = True
            self._drawingEnded = True
        self._updateArea()

    def _undoPart(self):
        if self.__deletedPart is None:
            return
        data = self.__deletedPart
        self.__deletedPart = None
        self.btnUndoPart.setEnabled(False)

        for band in self._completedBands.values():
            band.reset()
            band.hide()
        self._completedBands.clear()

        self.parts.insert(data["row"], list(data["part"]))

        contour_num = 1
        ring_num = 1
        for i in range(len(self.parts)):
            if self.parts[i][0] > 0:
                self.parts[i][0] = contour_num
                contour_num += 1
            else:
                self.parts[i][0] = -ring_num
                ring_num += 1

        self.__contursCount = contour_num - 1
        self.__ringsCount = ring_num - 1

        new_idx = min(data["row"], len(self.parts) - 1)
        self._currentPartIndex = new_idx
        self._updatePartList()
        self._loadPartFromTool()
        if self.drawTool is not None and self._currentPoints:
            self.drawTool.isDrawing = False
            self.drawTool._drawingEnded = True
            self._drawingEnded = True
        self._updateArea()

    # ------------------------------------------------------------------
    # Copy / Paste / Swap / Add Row / Delete Row
    # ------------------------------------------------------------------
    def _copyCoords(self):
        pts = self._currentPoints
        selected = self.tblCoords.selectionModel().selectedRows()
        rows = sorted(set(idx.row() for idx in selected)) if selected else []

        if not rows:
            rows = list(range(self.tblCoords.rowCount()))

        lines = []
        for r in rows:
            x_item = self.tblCoords.item(r, 1)
            y_item = self.tblCoords.item(r, 2)
            x = x_item.data(Qt.ItemDataRole.UserRole) if x_item else ""
            y = y_item.data(Qt.ItemDataRole.UserRole) if y_item else ""
            lines.append(f"{x}\t{y}")

        QApplication.clipboard().setText("\n".join(lines))

    def _pasteCoords(self):
        pts = self._currentPoints
        text = QApplication.clipboard().text()
        if not text.strip():
            return

        lines = [ln for ln in text.strip().split("\n") if ln.strip()]
        selected = self.tblCoords.selectionModel().selectedRows()
        start_row = selected[0].row() if selected else self.tblCoords.rowCount()

        for i, line in enumerate(lines):
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            try:
                x = float(parts[0].replace(",", "."))
                y = float(parts[1].replace(",", "."))
            except ValueError:
                continue

            row = start_row + i
            if row < self.tblCoords.rowCount():
                self.tblCoords.item(row, 1).setText("%.2f" % x)
                self.tblCoords.item(row, 1).setData(Qt.ItemDataRole.UserRole, x)
                self.tblCoords.item(row, 2).setText("%.2f" % y)
                self.tblCoords.item(row, 2).setData(Qt.ItemDataRole.UserRole, y)
                newPt = self._toProjectCrs(x, y)
                if row < len(pts):
                    pts[row] = newPt
                    self.pointEdited.emit(row, newPt)
            else:
                pt = self._toProjectCrs(x, y)
                pts.append(pt)
                self.lblPointCount.setText("Vertices: %d" % len(pts))

        self._updateCoordList()
        self._updateArea()
        self._updateLength()

    def _swapXY(self):
        pts = self._currentPoints
        self.tblCoords.blockSignals(True)
        for r in range(self.tblCoords.rowCount()):
            x_item = self.tblCoords.item(r, 1)
            y_item = self.tblCoords.item(r, 2)
            if x_item and y_item:
                tmp = x_item.text()
                x_item.setText(y_item.text())
                y_item.setText(tmp)
        self.tblCoords.blockSignals(False)

        for pt in pts:
            pt_new = QgsPointXY(pt.y(), pt.x())
            idx = pts.index(pt)
            pts[idx] = pt_new

        self._updateArea()
        self._updateLength()
        self.vertexSelected.emit(0)

    def _addRow(self):
        pts = self._currentPoints
        selected = self.tblCoords.selectionModel().selectedRows()
        if selected:
            row = selected[0].row() + 1
        else:
            row = self.tblCoords.rowCount()

        self.tblCoords.insertRow(row)
        idx = self.tblCoords.item(row - 1, 0) if row > 0 else None
        num = int(idx.text()) + 1 if idx else row + 1

        item0 = QTableWidgetItem(str(num))
        item0.setFlags(item0.flags() & ~Qt.ItemFlag.ItemIsEditable)
        item0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tblCoords.setItem(row, 0, item0)
        self.tblCoords.setItem(row, 1, QTableWidgetItem("0.00"))
        self.tblCoords.setItem(row, 2, QTableWidgetItem("0.00"))

        pt = pts[row - 1] if row <= len(pts) else pts[-1]
        pts.insert(row, pt)
        self.lblPointCount.setText("Vertices: %d" % len(pts))

    def _deleteRow(self):
        pts = self._currentPoints
        selected = self.tblCoords.selectionModel().selectedRows()
        if not selected:
            return

        rows = sorted([idx.row() for idx in selected], reverse=True)
        for r in rows:
            if r < len(pts):
                pts.pop(r)
            self.tblCoords.removeRow(r)

        self._updateCoordList()
        self._updateArea()
        self._updateLength()
        self.lblPointCount.setText("Vertices: %d" % len(pts))

    def _formatCoords(self, point):
        if not self.featureCrs or not self.mapCanvas:
            return (point.x(), point.y())
        projectCrs = self.mapCanvas.mapSettings().destinationCrs()
        if projectCrs != self.featureCrs:
            try:
                if (
                    self._cachedTransformForward is None
                    or self._cachedTransformProjectCrs != projectCrs
                    or self._cachedTransformFeatureCrs != self.featureCrs
                ):
                    self._cachedTransformForward = QgsCoordinateTransform(
                        projectCrs, self.featureCrs, QgsProject.instance()
                    )
                    self._cachedTransformProjectCrs = projectCrs
                    self._cachedTransformFeatureCrs = self.featureCrs
                t = self._cachedTransformForward.transform(point)
                return (t.x(), t.y())
            except QgsCsException:
                pass
        return (point.x(), point.y())

    def _toProjectCrs(self, x, y):
        if not self.featureCrs or not self.mapCanvas:
            return QgsPointXY(x, y)
        projectCrs = self.mapCanvas.mapSettings().destinationCrs()
        if projectCrs != self.featureCrs:
            try:
                if (
                    self._cachedTransformReverse is None
                    or self._cachedTransformProjectCrs != projectCrs
                    or self._cachedTransformFeatureCrs != self.featureCrs
                ):
                    self._cachedTransformReverse = QgsCoordinateTransform(
                        self.featureCrs, projectCrs, QgsProject.instance()
                    )
                    self._cachedTransformProjectCrs = projectCrs
                    self._cachedTransformFeatureCrs = self.featureCrs
                return self._cachedTransformReverse.transform(QgsPointXY(x, y))
            except QgsCsException:
                pass
        return QgsPointXY(x, y)

    def _invalidateTransformCache(self):
        self._cachedTransformForward = None
        self._cachedTransformReverse = None
        self._cachedTransformProjectCrs = None
        self._cachedTransformFeatureCrs = None

    def _updateCoordList(self, incremental=False):
        pts = self._currentPoints
        self.tblCoords.blockSignals(True)
        if incremental and self.tblCoords.rowCount() == len(pts) - 1:
            i = len(pts) - 1
            pt = pts[i]
            x, y = self._formatCoords(pt)
            self.tblCoords.insertRow(i)
            item0 = QTableWidgetItem(str(i + 1))
            item0.setFlags(item0.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tblCoords.setItem(i, 0, item0)
            itemX = QTableWidgetItem("%.2f" % x)
            itemX.setData(Qt.ItemDataRole.UserRole, x)
            itemX.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            itemY = QTableWidgetItem("%.2f" % y)
            itemY.setData(Qt.ItemDataRole.UserRole, y)
            itemY.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            self.tblCoords.setItem(i, 1, itemX)
            self.tblCoords.setItem(i, 2, itemY)
        else:
            self.tblCoords.setRowCount(len(pts))
            for i, pt in enumerate(pts):
                x, y = self._formatCoords(pt)
                item0 = QTableWidgetItem(str(i + 1))
                item0.setFlags(item0.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tblCoords.setItem(i, 0, item0)
                itemX = QTableWidgetItem("%.2f" % x)
                itemX.setData(Qt.ItemDataRole.UserRole, x)
                itemX.setTextAlignment(
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                )
                itemY = QTableWidgetItem("%.2f" % y)
                itemY.setData(Qt.ItemDataRole.UserRole, y)
                itemY.setTextAlignment(
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                )
                self.tblCoords.setItem(i, 1, itemX)
                self.tblCoords.setItem(i, 2, itemY)
        self.tblCoords.blockSignals(False)

    def _onCellClicked(self, row, col):
        pts = self._currentPoints
        if 0 <= row < len(pts):
            self.vertexSelected.emit(row)

    def _onCellEdited(self, row, col):
        pts = self._currentPoints
        if col < 1 or row >= len(pts):
            return
        try:
            x = float(self.tblCoords.item(row, 1).text())
            y = float(self.tblCoords.item(row, 2).text())
            self.tblCoords.item(row, 1).setData(Qt.ItemDataRole.UserRole, x)
            self.tblCoords.item(row, 2).setData(Qt.ItemDataRole.UserRole, y)
            newPt = self._toProjectCrs(x, y)
            pts[row] = newPt
            self._updateArea()
            self._updateLength()
            self.pointEdited.emit(row, newPt)
            if self.drawTool is not None:
                self.drawTool.updatePoint(row, newPt)
        except (ValueError, TypeError):
            pass

    def clearPoints(self):
        for band in self._completedBands.values():
            band.reset()
            band.hide()
        self._completedBands.clear()

        self.parts = [[1, []]]
        self._currentPartIndex = 0
        self.__contursCount = 1
        self.__ringsCount = 0
        self.__deletedPart = None
        self.btnUndoPart.setEnabled(False)
        self._previewPt = None
        self._drawingEnded = False
        self.lblPointCount.setText("Vertices: 0")
        self.tblCoords.setRowCount(0)
        self.lblArea.setText("Area: \u2014")
        self.areaFrame.hide()
        self.areaSeparator.hide()
        self.lblTotalArea.hide()
        self.lblLength.setText("Length: \u2014")
        self.lengthFrame.hide()
        self._updatePartList()

    # ------------------------------------------------------------------
    # Drawing actions
    # ------------------------------------------------------------------
    def restartDrawing(self):
        self.restartRequested.emit()

    def _onEndDrawing(self):
        pts = self._currentPoints
        if len(pts) >= self._minPoints():
            if self.geomType == "polygon":
                self.sortCoordinatesClockwise()
            self.clearPreviewPoint()
            self._drawingEnded = True
            self.drawingEnded.emit()

    def finishDrawing(self):
        self._commitCurrentPartToTool()
        if len(self._currentPoints) >= self._minPoints():
            self.finishedDrawing.emit(self.parts)

    def setPreviewPoint(self, point):
        self._previewPt = point
        self._pendingAreaPreview = True
        if not self._areaTimer.isActive():
            self._areaTimer.start()

    def clearPreviewPoint(self):
        self._previewPt = None
        self._pendingAreaPreview = False
        self._updateArea(use_preview=False)
        self._updateLength(use_preview=False)

    def _doDeferredAreaUpdate(self):
        if self._pendingAreaPreview:
            self._pendingAreaPreview = False
            self._updateArea(use_preview=True)
            self._updateLength(use_preview=True)

    # ------------------------------------------------------------------
    # Area calculation (multi-part: sum exteriors, subtract rings)
    # ------------------------------------------------------------------
    _AREA_UNITS = {
        "Hectares": (10000, "ha"),
        "Acres": (4046.8564224, "ac"),
        "Square Feet": (0.09290304, "ft\u00b2"),
        "Square Meters": (1.0, "m\u00b2"),
        "Square Kilometers": (1e6, "km\u00b2"),
        "Square Miles": (2589988.110336, "mi\u00b2"),
    }

    def _convertArea(self, area_sqm):
        unit = self.cbAreaUnit.currentText()
        divisor, symbol = self._AREA_UNITS[unit]
        return (
            f"{area_sqm / divisor:,.2f}".translate(str.maketrans(",.", ".,"))
            + f" {symbol}"
        )

    def _onAreaUnitChanged(self, _index):
        if self._area_sqm > 0:
            self.lblArea.setText(f"Area: {self._convertArea(self._area_sqm)}")
        if self._area_total_sqm > 0:
            self.lblTotalArea.setText(
                f"Total: {self._convertArea(self._area_total_sqm)}"
            )

    def _buildPartGeom(self, part_entry, ring_entries):
        """Build a QgsPolygon for a single exterior part with its rings."""
        if len(part_entry[1]) < 3:
            return None
        feature_pts = []
        for p in part_entry[1]:
            x, y = self._formatCoords(p)
            feature_pts.append(QgsPointXY(x, y))
        ring = QgsLineString(feature_pts)
        ring.close()
        poly = QgsPolygon()
        poly.setExteriorRing(ring)
        for ring_entry in ring_entries:
            if len(ring_entry[1]) < 3:
                continue
            ring_pts = []
            for p in ring_entry[1]:
                x, y = self._formatCoords(p)
                ring_pts.append(QgsPointXY(x, y))
            interior = QgsLineString(ring_pts)
            interior.close()
            poly.addInteriorRing(interior)
        return QgsGeometry(poly)

    def _calcPartArea(self, geom, da):
        if geom is None or geom.isEmpty():
            return 0.0
        a = da.measureArea(geom)
        return a if a >= 0 else -a

    def _updateArea(self, use_preview=False):
        self.areaFrame.hide()
        self.areaSeparator.hide()
        self.lblTotalArea.hide()
        self._area_sqm = 0.0
        self._area_total_sqm = 0.0
        if self.geomType != "polygon":
            return
        if not self.mapCanvas or not self.featureCrs:
            return

        preview_injected = False
        try:
            da = QgsDistanceArea()
            da.setSourceCrs(
                self.featureCrs, QgsProject.instance().transformContext()
            )
            if self.featureCrs.isGeographic():
                da.setEllipsoid(QgsProject.instance().ellipsoid())

            # Determine which part index is the active one (for preview injection)
            current_row = self._currentPartIndex
            preview_ext_idx = None
            if (
                use_preview
                and self._previewPt is not None
                and 0 <= current_row < len(self.parts)
                and self.parts[current_row][0] > 0
            ):
                preview_ext_idx = current_row

            # Temporarily inject preview point into the current part
            if preview_ext_idx is not None:
                self.parts[preview_ext_idx][1].append(self._previewPt)
                preview_injected = True

            # Collect exterior indices and their associated rings
            ext_indices = []
            for i, (part_num, _) in enumerate(self.parts):
                if part_num > 0 and len(self.parts[i][1]) >= 3:
                    ext_indices.append(i)

            if not ext_indices:
                return

            # Compute per-part area and total
            total_area = 0.0
            part_areas = []

            for ext_idx in ext_indices:
                next_ext = min(
                    (i for i in ext_indices if i > ext_idx),
                    default=len(self.parts),
                )
                rings = []
                for ri in range(ext_idx + 1, next_ext):
                    if (
                        self.parts[ri][0] < 0
                        and len(self.parts[ri][1]) >= 3
                    ):
                        rings.append(self.parts[ri])
                geom = self._buildPartGeom(self.parts[ext_idx], rings)
                area = self._calcPartArea(geom, da)
                total_area += area
                part_areas.append((ext_idx, area))

            self._area_total_sqm = total_area

            # Show current part's area
            if current_row >= 0 and current_row < len(self.parts):
                part_num = self.parts[current_row][0]
                if part_num > 0 and len(self.parts[current_row][1]) >= 3:
                    next_ext = min(
                        (i for i in ext_indices if i > current_row),
                        default=len(self.parts),
                    )
                    rings = []
                    for ri in range(current_row + 1, next_ext):
                        if (
                            self.parts[ri][0] < 0
                            and len(self.parts[ri][1]) >= 3
                        ):
                            rings.append(self.parts[ri])
                    geom = self._buildPartGeom(
                        self.parts[current_row], rings
                    )
                    self._area_sqm = self._calcPartArea(geom, da)
                    label = ""
                    if len(ext_indices) > 1:
                        label = "Part %d: " % part_num
                    self.lblArea.setText(
                        f"{label}{self._convertArea(self._area_sqm)}"
                    )
                    self.areaFrame.show()
                elif part_num < 0:
                    # Show parent part area
                    for i in range(current_row - 1, -1, -1):
                        if self.parts[i][0] > 0:
                            next_ext = min(
                                (j for j in ext_indices if j > i),
                                default=len(self.parts),
                            )
                            rings = []
                            for ri in range(i + 1, next_ext):
                                if (
                                    self.parts[ri][0] < 0
                                    and len(self.parts[ri][1]) >= 3
                                ):
                                    rings.append(self.parts[ri])
                            geom = self._buildPartGeom(self.parts[i], rings)
                            self._area_sqm = self._calcPartArea(geom, da)
                            label = ""
                            if len(ext_indices) > 1:
                                label = "Part %d: " % self.parts[i][0]
                            self.lblArea.setText(
                                f"{label}{self._convertArea(self._area_sqm)}"
                            )
                            self.areaFrame.show()
                            break

            # Show total if multiple exterior parts
            if total_area > 0 and len(ext_indices) > 1:
                self.areaSeparator.show()
                self.lblTotalArea.setText(
                    "Total: %s" % self._convertArea(total_area)
                )
                self.lblTotalArea.show()

        except Exception:
            self.lblArea.setText("N/A")
        finally:
            if preview_injected:
                self.parts[preview_ext_idx][1].pop()

    # ------------------------------------------------------------------
    # Length calculation
    # ------------------------------------------------------------------
    _LENGTH_UNITS = {
        "Meters": (1.0, "m"),
        "Kilometers": (1000.0, "km"),
        "Feet": (0.3048, "ft"),
        "Miles": (1609.344, "mi"),
        "Yards": (0.9144, "yd"),
    }

    def _convertLength(self, length_m):
        unit = self.cbLengthUnit.currentText()
        divisor, symbol = self._LENGTH_UNITS[unit]
        return (
            f"{length_m / divisor:,.2f}".translate(str.maketrans(",.", ".,"))
            + f" {symbol}"
        )

    def _onLengthUnitChanged(self, _index):
        if self._length_m > 0:
            self.lblLength.setText(f"Length: {self._convertLength(self._length_m)}")

    def _updateLength(self, use_preview=False):
        pts = self._currentPoints
        self.lengthFrame.hide()
        self._length_m = 0.0
        if self.geomType != "line":
            return
        lst = list(pts)
        if use_preview and self._previewPt:
            lst = lst + [self._previewPt]
        if not self.mapCanvas or len(lst) < 2:
            return
        if not self.featureCrs:
            return
        try:
            feature_pts = []
            for pt in lst:
                x, y = self._formatCoords(pt)
                feature_pts.append(QgsPointXY(x, y))
            line = QgsLineString(feature_pts)
            geom = QgsGeometry(line)
            da = QgsDistanceArea()
            da.setSourceCrs(self.featureCrs, QgsProject.instance().transformContext())
            if self.featureCrs.isGeographic():
                da.setEllipsoid(QgsProject.instance().ellipsoid())
            self._length_m = da.measureLength(geom)
            self.lblLength.setText(f"Length: {self._convertLength(self._length_m)}")
            self.lengthFrame.show()
        except Exception:
            self.lblLength.setText("N/A")

    # ------------------------------------------------------------------
    def closeEvent(self, event):
        super().closeEvent(event)
