import datetime

from PySide2.QtCore import Qt, QPropertyAnimation, QByteArray
from PySide2.QtGui import QColor
from PySide2.QtWidgets import *


class TargetsDock(QDockWidget):
    def __init__(self, parent, error, log):
        super().__init__(parent)
        self.parent = parent
        self.error = error
        self.log = log
        self.dockWidgetContentsTargets = QWidget()
        self.TargetSendToStageButton = QPushButton(self.dockWidgetContentsTargets)
        self.CreateGroupButton = QPushButton(self.dockWidgetContentsTargets)
        self.ClearSelectedTargetsButton = QPushButton(self.dockWidgetContentsTargets)
        self.TargetsButtonLayout = QHBoxLayout()
        self.TargetTree = QTreeWidget(self.dockWidgetContentsTargets)
        self.verticalLayout = QVBoxLayout(self.dockWidgetContentsTargets)
        self.setup_ui()

    def setup_ui(self):
        self.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)

        __qtreewidgetitem = QTreeWidgetItem(self.TargetTree)
        __qtreewidgetitem.setFlags(
            Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsTristate)
        __qtreewidgetitem1 = QTreeWidgetItem(self.TargetTree)
        __qtreewidgetitem1.setFlags(
            Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsTristate)

        self.TargetTree.setSortingEnabled(True)
        self.TargetTree.setAnimated(False)
        self.TargetTree.setAllColumnsShowFocus(False)
        self.TargetTree.setHeaderHidden(False)
        self.TargetTree.setColumnCount(2)

        self.TargetsButtonLayout.addWidget(self.ClearSelectedTargetsButton)
        self.TargetsButtonLayout.addWidget(self.CreateGroupButton)
        self.TargetsButtonLayout.addWidget(self.TargetSendToStageButton)

        self.verticalLayout.addWidget(self.TargetTree)
        self.verticalLayout.addLayout(self.TargetsButtonLayout)

        self.setWidget(self.dockWidgetContentsTargets)
        self.setup_ui_connections()
        self.setup_ui_text()

    def setup_ui_text(self):
        self.setWindowTitle("Targets")
        ___qtreewidgetitem = self.TargetTree.headerItem()
        ___qtreewidgetitem.setText(1, "Last Call")
        ___qtreewidgetitem.setText(0, "Target")

        __sortingEnabled = self.TargetTree.isSortingEnabled()
        self.TargetTree.setSortingEnabled(False)
        ___qtreewidgetitem1 = self.TargetTree.topLevelItem(0)
        ___qtreewidgetitem1.setText(1, "12:31 4/16/2020")
        ___qtreewidgetitem1.setText(0, "192.168.1.1")
        ___qtreewidgetitem1.setFlags(___qtreewidgetitem1.flags() | Qt.ItemIsUserCheckable)
        ___qtreewidgetitem1.setCheckState(0, Qt.Unchecked)
        ___qtreewidgetitem2 = self.TargetTree.topLevelItem(1)
        ___qtreewidgetitem2.setText(1, "12:32 4/16/2020")
        ___qtreewidgetitem2.setText(0, "10.10.10.10")
        ___qtreewidgetitem2.setFlags(___qtreewidgetitem1.flags() | Qt.ItemIsUserCheckable)
        ___qtreewidgetitem2.setCheckState(0, Qt.Unchecked)
        self.TargetTree.setSortingEnabled(__sortingEnabled)

        self.ClearSelectedTargetsButton.setText("Clear Selected")
        self.CreateGroupButton.setText("Create Group")
        self.TargetSendToStageButton.setText("Send To Stage")

    def setup_ui_connections(self):
        self.TargetSendToStageButton.clicked.connect(self.send_to_stage)
        self.CreateGroupButton.clicked.connect(self.create_group)
        self.ClearSelectedTargetsButton.clicked.connect(self.clear_selection)

    def send_to_stage(self):
        root = self.TargetTree.invisibleRootItem()
        num = root.childCount()
        to_send = list()
        for i in range(num):
            child = root.child(i)
            if child.checkState(0):
                to_send.append(child)

        for c in to_send:
            self.parent.stage_dock.add_target(c.text(0))

    def create_group(self):
        text, ok = QInputDialog.getText(self, 'Group Add', 'Enter a group name:')
        if ok and text.strip() != '':
            item = QTreeWidgetItem()
            item.setText(0, text)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Unchecked)

            root = self.TargetTree.invisibleRootItem()
            num = root.childCount()
            one_selected = False
            for i in range(num):
                child = root.child(i)
                if child.checkState(0):
                    one_selected = True
                    c = QTreeWidgetItem()
                    c.setText(0, child.text(0))
                    item.addChild(c)
            if one_selected:
                self.parent.groups_dock.add_group(item)
            else:
                self.error('No targets selected to form group')
        else:
            self.error('Group name required')

    def clear_selection(self):
        root = self.TargetTree.invisibleRootItem()
        num = root.childCount()
        for i in range(num):
            child = root.child(i)
            child.setCheckState(0, Qt.Unchecked)

    def add_target(self, target):
        root = self.TargetTree.invisibleRootItem()
        num = root.childCount()
        for i in range(num):
            child = root.child(i)
            if child.text(0) == target:
                child.setText(1, datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
                return
        item = QTreeWidgetItem()
        item.setText(0, target)
        item.setText(1, datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(0, Qt.Unchecked)
        self.TargetTree.addTopLevelItem(item)
