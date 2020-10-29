from PySide2.QtCore import QSize, Qt
from PySide2.QtWidgets import *
import json


class StageDock(QDockWidget):
    def __init__(self, parent, error, log):
        super().__init__(parent)
        self.parent = parent
        self.error = error
        self.log = log
        self.dockWidgetContents = QWidget()
        self.ClearStageButton = QPushButton(self.dockWidgetContents)
        self.StageButton = QPushButton(self.dockWidgetContents)
        self.lineEdit = QLineEdit(self.dockWidgetContents)
        self.horizontalLayout_2 = QHBoxLayout()
        self.RemoveCommandButton = QPushButton(self.dockWidgetContents)
        self.AddCommandButton = QPushButton(self.dockWidgetContents)
        self.CommandToAdd = QLineEdit(self.dockWidgetContents)
        self.horizontalLayout_3 = QHBoxLayout()
        self.CommandList = QTreeWidget(self.dockWidgetContents)
        self.verticalLayout_6 = QVBoxLayout()
        self.TargetList = QTreeWidget(self.dockWidgetContents)
        self.horizontalLayout = QHBoxLayout()
        self.verticalLayout_5 = QVBoxLayout(self.dockWidgetContents)
        self.setup_ui()

    def setup_ui(self):
        self.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.TargetList.setMaximumSize(QSize(300, 16777215))

        self.horizontalLayout.addWidget(self.TargetList)

        self.verticalLayout_6.addWidget(self.CommandList)

        self.horizontalLayout_3.addWidget(self.CommandToAdd)
        self.horizontalLayout_3.addWidget(self.AddCommandButton)
        self.horizontalLayout_3.addWidget(self.RemoveCommandButton)

        self.verticalLayout_6.addLayout(self.horizontalLayout_3)

        self.horizontalLayout.addLayout(self.verticalLayout_6)

        self.verticalLayout_5.addLayout(self.horizontalLayout)

        self.horizontalLayout_2.addWidget(self.lineEdit)
        self.horizontalLayout_2.addWidget(self.StageButton)
        self.horizontalLayout_2.addWidget(self.ClearStageButton)

        self.verticalLayout_5.addLayout(self.horizontalLayout_2)

        self.setWidget(self.dockWidgetContents)
        self.setup_ui_connections()
        self.setup_ui_text()

    def setup_ui_text(self):
        self.setWindowTitle("Stage")
        self.TargetList.headerItem().setText(0, "Targets")
        self.CommandList.headerItem().setText(0, "Commands")
        self.CommandToAdd.setPlaceholderText("Command")
        self.AddCommandButton.setText("Add Command")
        self.RemoveCommandButton.setText("Remove Command")
        self.lineEdit.setPlaceholderText("Stage Name")
        self.StageButton.setText("Stage")
        self.ClearStageButton.setText("Clear Stage")

    def setup_ui_connections(self):
        self.AddCommandButton.clicked.connect(self.add_command)
        self.RemoveCommandButton.clicked.connect(self.remove_command)
        self.ClearStageButton.clicked.connect(self.clear_stage)
        self.StageButton.clicked.connect(self.stage)

    def add_command(self):
        if self.CommandToAdd.text().strip() != '':
            item = QTreeWidgetItem(self.CommandList)
            item.setText(0, self.CommandToAdd.text())
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Unchecked)
            self.CommandToAdd.setText('')
            self.log(f'Command {item.text(0)} added')
        else:
            self.error('Enter a command first')

    def remove_command(self):
        root = self.CommandList.invisibleRootItem()
        num = root.childCount()
        to_remove = list()
        for i in range(num):
            child = root.child(i)
            if child.checkState(0):
                to_remove.append(child)

        for c in to_remove:
            root.removeChild(c)
            self.log(f'Command {c.text(0)} removed')

    def add_target(self, tar):
        root = self.TargetList.invisibleRootItem()
        num = root.childCount()
        for i in range(num):
            child = root.child(i)
            if child.text(0) == tar:
                return

        item = QTreeWidgetItem(self.TargetList)
        item.setText(0, tar)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(0, Qt.Unchecked)
        self.log(f'Target {tar} added to stage')

    def add_group(self, tar):
        root = self.TargetList.invisibleRootItem()
        num = root.childCount()
        for i in range(num):
            child = root.child(i)
            if child.text(0) == tar.text(0):
                return
        self.TargetList.addTopLevelItem(tar)
        self.log(f'Group {tar.text(0)} added to stage')

    def clear_stage(self):
        self.CommandList.invisibleRootItem().takeChildren()
        self.TargetList.invisibleRootItem().takeChildren()
        self.lineEdit.setText('')
        self.log('Stage cleared')

    def stage(self):
        if self.lineEdit.text().strip() == '':
            self.error('Stage name required')
            return
        name = self.lineEdit.text()
        item = QTreeWidgetItem()
        item.setText(0, name)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(0, Qt.Unchecked)

        targets = QTreeWidgetItem(item)
        targets.setText(0, 'TARGETS')
        root = self.TargetList.invisibleRootItem()
        num = root.childCount()
        d = {
            name: {
                'TARGETS': {},
                'COMMANDS': {}
            }
        }
        if num == 0:
            self.error('Add targets to the stage')
            return
        for i in range(num):
            child = root.child(i)
            targets.addChild(child.clone())
            d[name]['TARGETS'][child.text(0)] = {}
            if child.childCount() != 0:
                for j in range(child.childCount()):
                    d[name]['TARGETS'][child.text(0)][child.child(j).text(0)] = {}

        commands = QTreeWidgetItem(item)
        commands.setText(0, 'COMMANDS')
        root = self.CommandList.invisibleRootItem()
        num = root.childCount()
        if num == 0:
            self.error('Add commands to the stage')
            return
        for i in range(num):
            child = root.child(i)
            commands.addChild(child.clone())
            d[name]['COMMANDS'][child.text(0)] = {}

        self.parent.execution_dock.add_stage(item)
        self.clear_stage()
        self.parent.connection.send(f'STAGE ADD {json.dumps(d)}')

    def edit_staged_stage(self, item):
        target_item = item.child(0)
        command_item = item.child(1)
        self.clear_stage()
        for i in range(target_item.childCount()):
            tar = target_item.child(i)
            temp = QTreeWidgetItem()
            temp.setText(0, tar.text(0))
            children = tar.takeChildren()
            for child in children:
                temp.addChild(child.clone())
            tar.addChildren(children)
            temp.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            temp.setCheckState(0, Qt.Unchecked)
            self.TargetList.addTopLevelItem(temp)

        for i in range(command_item.childCount()):
            tar = command_item.child(i)
            temp = QTreeWidgetItem()
            temp.setText(0, tar.text(0))
            children = tar.takeChildren()
            for child in children:
                temp.addChild(child.clone())
            tar.addChildren(children)
            temp.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            temp.setCheckState(0, Qt.Unchecked)
            self.CommandList.addTopLevelItem(temp)

        self.lineEdit.setText(item.text(0))

