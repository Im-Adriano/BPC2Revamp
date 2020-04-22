from PySide2.QtWidgets import *


class ResponsesDock(QDockWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.dockWidgetContentsLogs = QWidget()
        self.TargetChooser = QComboBox(self.dockWidgetContentsLogs)
        self.ResponsesOutput = QTextBrowser(self.dockWidgetContentsLogs)
        self.verticalLayout_3 = QVBoxLayout(self.dockWidgetContentsLogs)
        self.setup_ui()

    def setup_ui(self):
        self.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.verticalLayout_3.addWidget(self.TargetChooser)
        self.verticalLayout_3.addWidget(self.ResponsesOutput)
        self.setWidget(self.dockWidgetContentsLogs)
        self.setup_ui_text()

    def setup_ui_text(self):
        self.setWindowTitle("Responses")
