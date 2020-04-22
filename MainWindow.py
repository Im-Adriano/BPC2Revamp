import json

from PySide2.QtCore import Qt, QTimer
from PySide2.QtWidgets import *

from Docks.ErrorDock import ErrorDock
from Docks.ExecutionDock import ExecutionDock
from Docks.GroupsDock import GroupDock
from Docks.LogsDock import LogsDock
from Docks.ResponsesDock import ResponsesDock
from Docks.StageDock import StageDock
from Docks.TargetsDock import TargetsDock
from Dialogs.RoomDialog import RoomDialog
from Dialogs.ServerDialog import ServerDialog
from Networking.client import Client
from Utils.TreeConversion import *


class MainWindow(QMainWindow):
    def __init__(self, udp_listen_port):
        super().__init__()
        self.connection = None
        self.udp_port = udp_listen_port
        self.ask_for_server_info()
        self.logs_dock = LogsDock(self)
        self.error_dock = ErrorDock(self)
        self.responses_dock = ResponsesDock(self)
        self.stage_dock = StageDock(self, self.error_dock.error, self.logs_dock.log)
        self.groups_dock = GroupDock(self, self.error_dock.error, self.logs_dock.log)
        self.targets_dock = TargetsDock(self, self.error_dock.error, self.logs_dock.log)
        self.execution_dock = ExecutionDock(self, self.error_dock.error, self.logs_dock.log)
        self.updateFromServerTimer = QTimer(self)
        self.save_action = QAction('Save', self)
        self.load_action = QAction('Load', self)
        self.file_menu = self.menuBar().addMenu('File')
        self.setup_ui()
        self.updateFromServerTimer.start()

    def setup_ui(self):
        if not self.objectName():
            self.setObjectName(u"self")
        self.resize(1096, 718)
        self.setDockOptions(
            QMainWindow.AllowNestedDocks | QMainWindow.AllowTabbedDocks | QMainWindow.AnimatedDocks)
        self.setCentralWidget(None)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.load_action)
        self.addDockWidget(Qt.TopDockWidgetArea, self.targets_dock)
        self.addDockWidget(Qt.TopDockWidgetArea, self.stage_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.logs_dock)
        self.splitDockWidget(self.logs_dock, self.responses_dock, Qt.Horizontal)
        self.splitDockWidget(self.logs_dock, self.error_dock, Qt.Vertical)
        self.splitDockWidget(self.targets_dock, self.groups_dock, Qt.Horizontal)
        self.splitDockWidget(self.stage_dock, self.execution_dock, Qt.Vertical)
        self.updateFromServerTimer.setInterval(10)
        self.updateFromServerTimer.timeout.connect(self.update_from_server)
        self.save_action.triggered.connect(self.save)
        self.load_action.triggered.connect(self.load)
        self.setup_ui_text()

    def setup_ui_text(self):
        self.setWindowTitle("BP C2")

    def closeEvent(self, event):
        self.connection.cleanup()

    def save(self):
        staged_commands = model_to_dict(self.execution_dock.StagedCommandsTree.model())
        groups = model_to_dict(self.groups_dock.GroupsTree.model())
        targets = model_to_dict(self.targets_dock.TargetTree.model())
        with open('staged_commands.json', 'w', encoding='utf-8') as f:
            json.dump(staged_commands, f, ensure_ascii=False, indent=4)
        with open('groups.json', 'w', encoding='utf-8') as f:
            json.dump(groups, f, ensure_ascii=False, indent=4)
        with open('targets.json', 'w', encoding='utf-8') as f:
            json.dump(targets, f, ensure_ascii=False, indent=4)

    def load(self):
        try:
            with open('staged_commands.json', 'r', encoding='utf-8') as f:
                staged_commands = json.load(f)
                self.execution_dock.StagedCommandsTree.invisibleRootItem().takeChildren()
                fill_model_from_json(self.execution_dock.StagedCommandsTree.invisibleRootItem(), staged_commands)
                root = self.execution_dock.StagedCommandsTree.invisibleRootItem()
                num = root.childCount()
                for i in range(num):
                    child = root.child(i)
                    child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                    child.setCheckState(0, Qt.Unchecked)
        except Exception as e:
            self.error_dock.error(e)
        try:
            with open('groups.json', 'r', encoding='utf-8') as f:
                groups = json.load(f)
                self.groups_dock.GroupsTree.invisibleRootItem().takeChildren()
                fill_model_from_json(self.groups_dock.GroupsTree.invisibleRootItem(), groups)
                root = self.groups_dock.GroupsTree.invisibleRootItem()
                num = root.childCount()
                for i in range(num):
                    child = root.child(i)
                    child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                    child.setCheckState(0, Qt.Unchecked)
        except Exception as e:
            self.error_dock.error(e)
        try:
            with open('targets.json', 'r', encoding='utf-8') as f:
                targets = json.load(f)
                self.targets_dock.TargetTree.invisibleRootItem().takeChildren()
                fill_model_from_json(self.targets_dock.TargetTree.invisibleRootItem(), targets)
                root = self.targets_dock.TargetTree.invisibleRootItem()
                num = root.childCount()
                for i in range(num):
                    child = root.child(i)
                    child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                    child.setCheckState(0, Qt.Unchecked)
        except Exception as e:
            self.error_dock.error(e)

    def update_from_server(self):
        messages = self.connection.get_messages()
        if len(messages) != 0:
            print(messages)
            for message in messages:
                message = json.loads(message.decode())
                if 'Target' in message:
                    target = message.split(' ')[1]
                    self.targets_dock.add_target(target)

    def ask_for_server_info(self):
        good = False
        while not good:
            good, autojoin, ip, port = ServerDialog().get_results()
            if good:
                try:
                    self.connection = Client(ip, port, port, self.udp_port)
                except Exception as e:
                    print(e)
                    good = False
            else:
                exit()
        if not autojoin:
            rooms = self.connection.get_rooms()
            rooms = [room['id'] for room in rooms]
            good = False
            while not good:
                good, create, room = RoomDialog(rooms).get_results()
                if good and create:
                    self.connection.create_room(room)
                elif good:
                    self.connection.join_room(room)
                else:
                    exit()
        else:
            self.connection.autojoin()
