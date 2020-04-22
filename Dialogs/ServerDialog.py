from PySide2.QtCore import Qt
from PySide2.QtWidgets import *


class ServerDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.buttonBox = QDialogButtonBox(self)
        self.AutojoinCheckbox = QCheckBox(self)
        self.ServerPortInput = QLineEdit(self)
        self.ServerIPInput = QLineEdit(self)
        self.verticalLayout = QVBoxLayout(self)
        self.setup_ui()

    def setup_ui(self):
        self.resize(260, 116)

        self.verticalLayout.addWidget(self.ServerIPInput)

        self.verticalLayout.addWidget(self.ServerPortInput)

        self.verticalLayout.addWidget(self.AutojoinCheckbox)

        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)

        self.setup_ui_text()
        self.setup_ui_connections()

    def setup_ui_text(self):
        self.setWindowTitle("Server Setup")
        self.ServerIPInput.setPlaceholderText("Server IP")
        self.ServerPortInput.setPlaceholderText("Server Port")
        self.AutojoinCheckbox.setText("Auto join a room")

    def setup_ui_connections(self):
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def get_results(self):
        if self.exec_() == self.Accepted:
            if self.ServerIPInput.text().strip() == '' or self.ServerPortInput.text().strip() == '':
                return False, None, None, None
            try:
                port = int(self.ServerPortInput.text().strip())
                return True, self.AutojoinCheckbox.isChecked(), self.ServerIPInput.text().strip(), port
            except ValueError:
                return False, None, None, None
        else:
            return False, None, None, None
