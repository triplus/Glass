# Glass module for FreeCAD
# Copyright (C) 2018, 2020 triplus @ FreeCAD
#
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

"""Glass module for FreeCAD - Gui."""


import FreeCADGui as Gui
import FreeCAD
from PySide import QtGui
from PySide import QtCore

mode = 0
wid = QtGui.QWidget()
mw = Gui.getMainWindow()
p = FreeCAD.ParamGet("User parameter:BaseApp/Glass")


try:
    mw.setDockOptions(mw.dockOptions() | mw.GroupedDragging)
except AttributeError:
    pass


def firstRun():
    """Setup defaults on the first run."""
    pTree = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/DockWindows/TreeView")
    pTree.SetBool("Enabled", True)

    #pStyle = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/MainWindow")
    #pStyle.SetString("StyleSheet", "Dark-blue.qss")

    #pView = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View")
    #pView.SetUnsigned("BackgroundColor2", 1852731135)
    #pView.SetUnsigned("BackgroundColor3", 2829625599)
    #pView.SetUnsigned("BackgroundColor4", 1852731135)


def findDock():
    """Find combo view widget."""
    global dock
    dock = mw.findChild(QtGui.QDockWidget, "Tree view")


def createActions():
    """Create actions."""
    a1 = QtGui.QAction(mw)
    a1.setParent(mw)
    a1.setText("Glass toggle dock mode")
    a1.setObjectName("GlassToggleMode")
    a1.setShortcut(QtGui.QKeySequence("Q, 1"))
    a1.triggered.connect(setMode)
    mw.addAction(a1)
    a2 = QtGui.QAction(mw)
    a2.setParent(mw)
    a2.setText("Glass toggle dock visibility")
    a2.setObjectName("GlassToggleVisibility")
    a2.setShortcut(QtGui.QKeySequence("Q, 2"))
    a2.triggered.connect(setVisibility)
    mw.addAction(a2)


def applyGlass(boolean, widget):
    """Apply or remove glass."""
    try:
        if boolean:
            widget.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        else:
            widget.setWindowFlags(dock.windowFlags() & ~QtCore.
                                  Qt.
                                  FramelessWindowHint)
    except:
        pass
    try:
        widget.setAttribute(QtCore.Qt.WA_NoSystemBackground, boolean)
    except:
        pass
    try:
        widget.setAttribute(QtCore.Qt.WA_TranslucentBackground, boolean)
    except:
        pass
    transparent_classes = [QtGui.QScrollBar, QtGui.QLineEdit, QtGui.QAbstractButton, QtGui.QHeaderView, QtGui.QDockWidget]
    
    if not p.GetString("TextColor"):
        p.SetString("TextColor", "black")
    
    pColor = p.GetString("TextColor")
    
    try:
        if boolean and (widget.__class__ in transparent_classes) or (widget.objectName() in ['qt_scrollarea_hcontainer', 'qt_scrollarea_vcontainer']):
            widget.setStyleSheet(f"background:transparent; border:none; color:{pColor};")
        else:
            widget.setStyleSheet(f"color:{pColor};")
    except:
        pass
    try:
        widget.setAutoFillBackground(boolean)
    except:
        pass
    try:
        if boolean:
            widget.setVerticalScrollBarPolicy((QtCore.Qt.ScrollBarAlwaysOff))
        else:
            widget.setVerticalScrollBarPolicy((QtCore.Qt.ScrollBarAsNeeded))
    except:
        pass
    try:
        if boolean:
            widget.setHorizontalScrollBarPolicy((QtCore.Qt.ScrollBarAlwaysOff))
        else:
            widget.setHorizontalScrollBarPolicy((QtCore.Qt.ScrollBarAsNeeded))
    except:
        pass
    try:
        widget.setDocumentMode(boolean)
    except:
        pass
    try:
        widget.tabBar().setDrawBase(False)
    except:
        pass
    try:
        if boolean:
            widget.header().hide()
        else:
            widget.header().show()
    except:
        pass


def widgetList(boolean):
    """List of child widgets."""
    children = []
    children.append(dock)

    child = True
    while child:
        child = False
        for i in children:
            if i.children():
                for c in i.children():
                    if c not in children:
                        children.append(c)
                        child = True

    for child in children:
        if isinstance(child, QtGui.QWidget):
            applyGlass(boolean, child)
    if boolean:
        dock.setStyleSheet("")

def setMode():
    """Set dock or overlay widget mode."""
    global mode
    mdi = mw.findChild(QtGui.QMdiArea)

    if mode == 0:
        dock.setParent(mdi)
        dock.setTitleBarWidget(wid)
        wid.hide()
        dock.show()
        widgetList(True)
        mode = 1
    else:
        dock.setParent(mw)
        dock.setTitleBarWidget(None)
        mw.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)
        dock.show()
        widgetList(False)
        mode = 0

    onResize()


def setVisibility():
    """Toggle visibility."""
    dock.toggleViewAction().trigger()


def onResize():
    """Resize dock."""
    mdi = mw.findChild(QtGui.QMdiArea)

    if mode == 1:
        x = 0
        y = 0
        w = mdi.geometry().width() / 100 * 15
        h = (mdi.geometry().height() -
             mdi.findChild(QtGui.QTabBar).geometry().height())
        dock.setGeometry(x, y, w, h)

    if str(Gui.activeView()) == "View3DInventor":
        dock.show()
    else:
        dock.hide()


def onStart():
    """Start the glass module."""
    if mw.property("eventLoop"):
        timer.stop()
        timer.timeout.disconnect(onStart)
        findDock()
        createActions()
        if p.GetBool("glassAuto", 1):
            setMode() # activate Glass mode
        timer.timeout.connect(onResize)
        timer.start(2000)


if p.GetBool("FirstRun", 1):
    """Setup defaults on the first run."""
    firstRun()
    p.SetBool("FirstRun", 0)


if (not FreeCAD.Version().__contains__("LinkStage3")):
    timer = QtCore.QTimer()
    timer.timeout.connect(onStart)
    timer.start(500)