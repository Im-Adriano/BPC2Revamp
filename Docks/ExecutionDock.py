from PySide2.QtGui import QStandardItemModel, Qt
from PySide2.QtWidgets import *

# from TreeConversion import fill_model_from_json, model_to_dict


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
        self.setup_ui()

    def setup_ui(self):
        self.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)

        # __qtreewidgetitem4 = QTreeWidgetItem(self.StagedCommandsTree)
        # __qtreewidgetitem5 = QTreeWidgetItem(__qtreewidgetitem4)
        # QTreeWidgetItem(__qtreewidgetitem5)
        # __qtreewidgetitem6 = QTreeWidgetItem(__qtreewidgetitem4)
        # QTreeWidgetItem(__qtreewidgetitem6)
        # temp = {'LS': {'TARGETS': {'192.168.1.1': {}, '10.10.10.10': {}}, 'COMMANDS': {'ls -la': {}}}, 'IP': {'TARGETS': {'LINUX': {'192.168.1.1': {}, '10.10.10.10': {}}}, 'COMMANDS': {'IP A': {}}}}
        # fill_model_from_json(self.StagedCommandsTree.invisibleRootItem(), temp)
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
        # self.StagedCommandsTree.model().setHeaderData(0, Qt.Horizontal, 'Stages')

        # __sortingEnabled2 = self.StagedCommandsTree.isSortingEnabled()
        # self.StagedCommandsTree.setSortingEnabled(False)
        # ___qtreewidgetitem11 = self.StagedCommandsTree.topLevelItem(0)
        # ___qtreewidgetitem11.setText(0, "IPCONFIG")
        # ___qtreewidgetitem12 = ___qtreewidgetitem11.child(0)
        # ___qtreewidgetitem12.setText(0, "TARGETS")
        # ___qtreewidgetitem13 = ___qtreewidgetitem12.child(0)
        # ___qtreewidgetitem13.setText(0, "10.10.10.10")
        # ___qtreewidgetitem14 = ___qtreewidgetitem11.child(1)
        # ___qtreewidgetitem14.setText(0, "COMMANDS")
        # ___qtreewidgetitem15 = ___qtreewidgetitem14.child(0)
        # ___qtreewidgetitem15.setText(0, "powershell.exe -c ipconfig")
        # self.StagedCommandsTree.setSortingEnabled(__sortingEnabled2)

        self.ExecuteButton.setText("Execute")
        self.PushButton.setText("Push")
        self.RemoveButton.setText("Remove")

    def setup_ui_connections(self):
        self.RemoveButton.clicked.connect(self.remove)

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

    def execute(self):
        pass

