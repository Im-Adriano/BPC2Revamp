from PySide2.QtCore import Qt
from PySide2.QtWidgets import *


class GroupDock(QDockWidget):
    def __init__(self, parent, error, log):
        super().__init__(parent)
        self.parent = parent
        self.error = error
        self.log = log
        self.dockWidgetContentsGroups = QWidget()
        self.SendGroupToStageButton = QPushButton(self.dockWidgetContentsGroups)
        self.DeleteGroupButton = QPushButton(self.dockWidgetContentsGroups)
        self.ClearSelectedGroupButton = QPushButton(self.dockWidgetContentsGroups)
        self.GroupsButtonLayout = QHBoxLayout()
        self.GroupsTree = QTreeWidget(self.dockWidgetContentsGroups)
        self.verticalLayout_2 = QVBoxLayout(self.dockWidgetContentsGroups)
        self.setup_ui()

    def setup_ui(self):
        self.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        # __qtreewidgetitem2 = QTreeWidgetItem(self.GroupsTree)
        # QTreeWidgetItem(__qtreewidgetitem2)
        # __qtreewidgetitem3 = QTreeWidgetItem(self.GroupsTree)
        # QTreeWidgetItem(__qtreewidgetitem3)
        self.GroupsTree.setSortingEnabled(True)

        self.GroupsButtonLayout.addWidget(self.ClearSelectedGroupButton)
        self.GroupsButtonLayout.addWidget(self.DeleteGroupButton)
        self.GroupsButtonLayout.addWidget(self.SendGroupToStageButton)

        self.verticalLayout_2.addWidget(self.GroupsTree)
        self.verticalLayout_2.addLayout(self.GroupsButtonLayout)

        self.setWidget(self.dockWidgetContentsGroups)
        self.setup_ui_connections()
        self.setup_ui_text()

    def setup_ui_text(self):
        self.setWindowTitle("Groups")
        ___qtreewidgetitem3 = self.GroupsTree.headerItem()
        ___qtreewidgetitem3.setText(0, "Groups")

        # __sortingEnabled1 = self.GroupsTree.isSortingEnabled()
        # self.GroupsTree.setSortingEnabled(False)
        # ___qtreewidgetitem4 = self.GroupsTree.topLevelItem(0)
        # ___qtreewidgetitem4.setText(0, "WINDOWS BOIS")
        # ___qtreewidgetitem4.setFlags(___qtreewidgetitem4.flags() | Qt.ItemIsUserCheckable)
        # ___qtreewidgetitem4.setCheckState(0, Qt.Unchecked)
        # ___qtreewidgetitem5 = ___qtreewidgetitem4.child(0)
        # ___qtreewidgetitem5.setText(0, "10.10.10.10")
        # ___qtreewidgetitem6 = self.GroupsTree.topLevelItem(1)
        # ___qtreewidgetitem6.setText(0, "LINUX BOIS")
        # ___qtreewidgetitem6.setFlags(___qtreewidgetitem6.flags() | Qt.ItemIsUserCheckable)
        # ___qtreewidgetitem6.setCheckState(0, Qt.Unchecked)
        # ___qtreewidgetitem7 = ___qtreewidgetitem6.child(0)
        # ___qtreewidgetitem7.setText(0, "192.168.1.1")
        # self.GroupsTree.setSortingEnabled(__sortingEnabled1)

        self.ClearSelectedGroupButton.setText("Clear Selected")
        self.DeleteGroupButton.setText("Delete")
        self.SendGroupToStageButton.setText("Send To Stage")

    def setup_ui_connections(self):
        self.DeleteGroupButton.clicked.connect(self.remove_group)
        self.SendGroupToStageButton.clicked.connect(self.send_to_stage)
        self.ClearSelectedGroupButton.clicked.connect(self.clear_selection)

    def add_group(self, group):
        self.GroupsTree.addTopLevelItem(group)
        self.log(f'Group {group.text(0)} created')

    def remove_group(self):
        root = self.GroupsTree.invisibleRootItem()
        num = root.childCount()
        to_remove = list()
        for i in range(num):
            child = root.child(i)
            if child.checkState(0):
                to_remove.append(child)

        for c in to_remove:
            root.removeChild(c)
            self.log(f'Group {c.text(0)} removed')

    def send_to_stage(self):
        root = self.GroupsTree.invisibleRootItem()
        num = root.childCount()
        to_send = list()
        for i in range(num):
            child = root.child(i)
            if child.checkState(0):
                to_send.append(child)

        for c in to_send:
            item = QTreeWidgetItem()
            item.setText(0, c.text(0))
            children = c.takeChildren()
            for child in children:
                item.addChild(child.clone())
            c.addChildren(children)
            self.parent.stage_dock.add_group(item)

    def clear_selection(self):
        root = self.GroupsTree.invisibleRootItem()
        num = root.childCount()
        for i in range(num):
            child = root.child(i)
            child.setCheckState(0, Qt.Unchecked)
