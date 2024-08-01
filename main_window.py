import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QAction, QToolBar, QPushButton
)

from modify_xml import XMLModifier
from merge_xmls import XMLMerger


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('XML File Manager')
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.xml_merger = XMLMerger()
        self.xml_modifier = XMLModifier()

        self.central_widget.addWidget(self.xml_merger)
        self.central_widget.addWidget(self.xml_modifier)

        self.createToolbar()

    def createToolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        switchToMergeButton = QPushButton('Merge XML Files')
        switchToMergeButton.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.xml_merger))
        toolbar.addWidget(switchToMergeButton)

        switchToModifyButton = QPushButton('Modify XML Files')
        switchToModifyButton.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.xml_modifier))
        toolbar.addWidget(switchToModifyButton)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())
