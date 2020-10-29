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

        self.GroupsTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.GroupsTree.customContextMenuRequested.connect(self.right_click_tree_node)
        self.GroupsTree.itemDoubleClicked.connect(self.left_click_tree_node)

        self.setup_ui()

    def setup_ui(self):
        self.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
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
        self.GroupsTree.headerItem().setText(0, "Groups")
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
            self.parent.connection.send(f'GROUP REMOVE {c.text(0)}')

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

    def right_click_tree_node(self, event):
        item = self.GroupsTree.itemAt(event)
        if item.childCount() > 0:
            num = item.childCount()
            get_responses = []
            for i in range(num):
                get_responses.append(item.child(i).text(0))
            self.parent.responses_dock.show_responses(get_responses)
        else:
            self.parent.responses_dock.show_responses([item.text(0)])

    def left_click_tree_node(self, item, _):
        if not item.parent():
            root = self.GroupsTree.invisibleRootItem()
            root.removeChild(item)
            self.log(f'Group {item.text(0)} removed for editing')
            self.parent.connection.send(f'GROUP REMOVE {item.text(0)}')
            self.parent.targets_dock.edit_group(item)

            del item
