import datetime

from PySide2.QtCore import Qt, QPropertyAnimation, QByteArray
from PySide2.QtGui import QColor
from PySide2.QtWidgets import *
import json


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

        self.TargetTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.TargetTree.customContextMenuRequested.connect(self.right_click_tree_node)

        self.setWidget(self.dockWidgetContentsTargets)
        self.setup_ui_connections()
        self.setup_ui_text()

    def setup_ui_text(self):
        self.setWindowTitle("Targets")
        self.TargetTree.headerItem().setText(1, "Last Call")
        self.TargetTree.headerItem().setText(0, "Target")
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
            d = {text: list()}
            for i in range(num):
                child = root.child(i)
                if child.checkState(0):
                    one_selected = True
                    c = QTreeWidgetItem()
                    c.setText(0, child.text(0))
                    item.addChild(c)
                    d[text].append(child.text(0))
            if one_selected:
                self.parent.groups_dock.add_group(item)
                self.parent.connection.send(f'GROUP ADD {json.dumps(d)}')
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

    def right_click_tree_node(self, event):
        item = self.TargetTree.itemAt(event)
        self.parent.responses_dock.show_responses([item.text(0)])

    def edit_group(self, item):
        self.clear_selection()
        root = self.TargetTree.invisibleRootItem()
        num = root.childCount()
        for i in range(item.childCount()):
            for j in range(num):
                child = root.child(j)
                if child.text(0) == item.child(i).text(0):
                    child.setCheckState(0, Qt.Checked)

