from PySide2.QtWidgets import *


class LogsDock(QDockWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.dockWidgetContentsLogs = QWidget()
        self.LogsOutput = QTextBrowser(self.dockWidgetContentsLogs)
        self.verticalLayout_3 = QVBoxLayout(self.dockWidgetContentsLogs)
        self.setup_ui()

    def setup_ui(self):
        self.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.verticalLayout_3.addWidget(self.LogsOutput)
        self.setWidget(self.dockWidgetContentsLogs)
        self.setup_ui_text()

    def setup_ui_text(self):
        self.setWindowTitle("Logs")

    def log(self, s):
        self.LogsOutput.append(str(s))
