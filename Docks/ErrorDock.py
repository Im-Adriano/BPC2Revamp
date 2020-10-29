from PySide2.QtWidgets import *


class ErrorDock(QDockWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.dockWidgetContentsErrorLogs = QWidget()
        self.ErrorLogsOutput = QTextBrowser(self.dockWidgetContentsErrorLogs)
        self.verticalLayout_4 = QVBoxLayout(self.dockWidgetContentsErrorLogs)
        self.setup_ui()

    def setup_ui(self):
        self.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.verticalLayout_4.addWidget(self.ErrorLogsOutput)
        self.setWidget(self.dockWidgetContentsErrorLogs)
        self.ErrorLogsOutput.setStyleSheet("color: red;")
        self.setup_ui_text()

    def setup_ui_text(self):
        self.setWindowTitle("Error Logs")

    def error(self, s):
        self.ErrorLogsOutput.append(str(s))
