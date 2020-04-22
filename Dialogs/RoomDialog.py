from PySide2.QtCore import QSize, Qt
from PySide2.QtGui import QFont
from PySide2.QtWidgets import *


class RoomDialog(QDialog):
    def __init__(self, rooms):
        super().__init__()
        self.buttonBox = QDialogButtonBox(self)
        self.roomName = QLineEdit(self)
        self.RoomsToJoin = QComboBox(self)
        self.horizontalLayout_2 = QHBoxLayout()
        self.createRoomButton = QRadioButton(self)
        self.joinRoomButton = QRadioButton(self)
        self.horizontalLayout = QHBoxLayout()
        self.label = QLabel(self)
        self.verticalLayout = QVBoxLayout(self)
        self.RoomsToJoin.addItems(rooms)
        self.setup_ui()

    def setup_ui(self):
        self.resize(600, 116)
        self.setMinimumSize(QSize(600, 0))
        self.setMaximumSize(QSize(600, 16777215))
        font = QFont()
        font.setPointSize(10)
        self.label.setFont(font)

        self.verticalLayout.addWidget(self.label)

        self.joinRoomButton.setChecked(True)

        self.horizontalLayout.addWidget(self.joinRoomButton)

        self.horizontalLayout.addWidget(self.createRoomButton)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2.addWidget(self.RoomsToJoin)

        self.roomName.setEnabled(False)
        self.roomName.setMaximumSize(QSize(300, 16777215))

        self.horizontalLayout_2.addWidget(self.roomName)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)

        self.setup_ui_text()
        self.setup_ui_connections()

    def setup_ui_text(self):
        self.setWindowTitle("Room Choice")
        self.label.setText("Create or Join a Room")
        self.joinRoomButton.setText("Join")
        self.createRoomButton.setText("Create")
        self.roomName.setPlaceholderText("Room Name")

    def setup_ui_connections(self):
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.createRoomButton.toggled.connect(self.roomName.setEnabled)
        self.joinRoomButton.toggled.connect(self.RoomsToJoin.setEnabled)

    def get_results(self):
        if self.exec_() == self.Accepted:
            if self.createRoomButton.isChecked() and self.roomName.text().strip() == '':
                return False, None, None
            elif not self.createRoomButton.isChecked() and self.RoomsToJoin.currentText() == '':
                return False, None, None
            elif self.createRoomButton.isChecked():
                return True, self.createRoomButton.isChecked(), self.roomName.text()
            else:
                return True, self.createRoomButton.isChecked(), str(self.RoomsToJoin.currentText())
        else:
            return False, None, None
