from PySide2.QtCore import Qt
from PySide2.QtWidgets import *


class ExecutionDock(QDockWidget):
    def __init__(self, parent, error, log):
        super().__init__(parent)
        self.parent = parent
        self.error = error
        self.log = log
        self.dockWidgetContents_2 = QWidget()
        self.RemoveButton = QPushButton(self.dockWidgetContents_2)
        self.PushButton = QPushButton(self.dockWidgetContents_2)
        self.ExecuteButton = QPushButton(self.dockWidgetContents_2)
        self.horizontalLayout_4 = QHBoxLayout()
        self.StagedCommandsTree = QTreeWidget(self.dockWidgetContents_2)
        self.verticalLayout_7 = QVBoxLayout(self.dockWidgetContents_2)

        self.StagedCommandsTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.StagedCommandsTree.customContextMenuRequested.connect(self.right_click_tree_node)
        self.StagedCommandsTree.itemDoubleClicked.connect(self.left_click_tree_node)

        self.setup_ui()

    def setup_ui(self):
        self.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.verticalLayout_7.addWidget(self.StagedCommandsTree)

        self.horizontalLayout_4.addWidget(self.ExecuteButton)
        self.horizontalLayout_4.addWidget(self.PushButton)
        self.horizontalLayout_4.addWidget(self.RemoveButton)

        self.verticalLayout_7.addLayout(self.horizontalLayout_4)

        self.setWidget(self.dockWidgetContents_2)
        self.setup_ui_connections()
        self.setup_ui_text()

    def setup_ui_text(self):
        self.setWindowTitle("Execution")
        self.StagedCommandsTree.headerItem().setText(0, "Stages")
        self.ExecuteButton.setText("Execute")
        self.PushButton.setText("Push")
        self.RemoveButton.setText("Remove")

    def setup_ui_connections(self):
        self.RemoveButton.clicked.connect(self.remove)
        self.PushButton.clicked.connect(self.push)
        self.ExecuteButton.clicked.connect(self.execute)

    def add_stage(self, stage):
        self.StagedCommandsTree.addTopLevelItem(stage)
        self.log(f'{stage.text(0)} added to execution')

    def remove(self):
        root = self.StagedCommandsTree.invisibleRootItem()
        num = root.childCount()
        to_remove = list()
        for i in range(num):
            child = root.child(i)
            if child.checkState(0):
                to_remove.append(child)

        for c in to_remove:
            root.removeChild(c)
            self.log(f'Stage {c.text(0)} removed from execution stage')
            self.parent.connection.send(f'STAGE REMOVE {c.text(0)}')

    def stages_to_dict(self):
        root = self.StagedCommandsTree.invisibleRootItem()
        num = root.childCount()
        to_stage = list()
        d = {}
        for i in range(num):
            child = root.child(i)
            if child.checkState(0):
                self.log(f'Sending {child.text(0)} to be executed')
                to_stage.append(child)

        for c in to_stage:
            targets = c.child(0)
            commands = c.child(1)
            for i in range(targets.childCount()):
                child = targets.child(i)
                if child.childCount() > 0:
                    # A Group
                    for j in range(child.childCount()):
                        tar = child.child(j).text(0)
                        if tar not in d:
                            d[tar] = list()
                        for k in range(commands.childCount()):
                            command = commands.child(k).text(0)
                            d[tar].append(command)
                else:
                    # Single IP
                    tar = child.text(0)
                    if tar not in d:
                        d[tar] = list()
                    for k in range(commands.childCount()):
                        command = commands.child(k).text(0)
                        d[tar].append(command)
        return d

    def execute(self):
        d = self.stages_to_dict()
        self.parent.connection.execute(d)

    def push(self):
        d = self.stages_to_dict()
        self.parent.connection.push(d)

    def right_click_tree_node(self, event):
        item = self.StagedCommandsTree.itemAt(event)
        num = item.childCount()
        if item.text(0) == 'COMMANDS':
            return
        if num > 0:
            get_responses = []
            for i in range(num):
                if item.child(i).text(0) != 'COMMANDS':
                    num2 = item.child(i).childCount()
                    if num2 > 0:
                        for j in range(num2):
                            num3 = item.child(i).child(j).childCount()
                            if num3 > 0:
                                for k in range(num3):
                                    get_responses.append(item.child(i).child(j).child(k).text(0))
                            else:
                                get_responses.append(item.child(i).child(j).text(0))
                    else:
                        get_responses.append(item.child(i).text(0))
            self.parent.responses_dock.show_responses(get_responses)
        else:
            self.parent.responses_dock.show_responses([item.text(0)])

    def left_click_tree_node(self, item, _):
        if not item.parent():
            root = self.StagedCommandsTree.invisibleRootItem()
            root.removeChild(item)
            self.log(f'Stage {item.text(0)} removed for editing from execution stage')
            self.parent.connection.send(f'STAGE REMOVE {item.text(0)}')
            self.parent.stage_dock.edit_staged_stage(item)

            del item

