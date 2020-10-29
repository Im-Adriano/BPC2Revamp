from PySide2.QtWidgets import *


class ResponsesDock(QDockWidget):
    def __init__(self, parent, error):
        super().__init__(parent)
        self.dockWidgetContentsLogs = QTabWidget()
        self.error = error
        self.responses = {'': ''}
        self.setup_ui()

    def setup_ui(self):
        self.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.setWidget(self.dockWidgetContentsLogs)
        self.setup_ui_text()

    def setup_ui_text(self):
        self.setWindowTitle("Responses")

    def show_responses(self, targets):
        self.dockWidgetContentsLogs.clear()
        for target in targets:
            wig = QWidget()
            self.dockWidgetContentsLogs.addTab(wig, target)
            layout = QVBoxLayout()
            text_box = QTextBrowser()
            layout.addWidget(text_box)
            try:
                for t in self.responses[target]:
                    text_box.append(t)
            except KeyError:
                self.error(f'No responses for: {target}')
            wig.setLayout(layout)
