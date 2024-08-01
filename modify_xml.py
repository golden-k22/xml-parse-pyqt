import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QFileDialog, QLineEdit, QLabel, QMessageBox, QHBoxLayout, QScrollArea, QTextEdit, QSplitter
)
from PyQt5.QtCore import Qt
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom


class XMLModifier(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XML Modifier")
        self.setGeometry(300, 300, 800, 600)

        self.splitter = QSplitter(Qt.Horizontal)

        # Left panel layout
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)

        self.open_button = QPushButton("Open XML File")
        self.open_button.clicked.connect(self.open_file_dialog)
        self.left_layout.addWidget(self.open_button)

        self.save_button = QPushButton("Save XML File")
        self.save_button.clicked.connect(self.save_file_dialog)
        self.save_button.setEnabled(False)
        self.left_layout.addWidget(self.save_button)

        self.scroll_area = QScrollArea()
        self.scroll_area_widget = QWidget()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.scroll_layout = QVBoxLayout(self.scroll_area_widget)
        self.left_layout.addWidget(self.scroll_area)

        self.splitter.addWidget(self.left_panel)

        # Right panel (text area)
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.splitter.addWidget(self.text_area)

        self.splitter.setSizes([300, 500])  # Adjust initial sizes

        self.setCentralWidget(self.splitter)

        self.xml_tree = None
        self.xml_root = None
        self.input_fields = {}

        # Set the working directory to the directory of the executable
        if hasattr(sys, '_MEIPASS'):
            os.chdir(sys._MEIPASS)
        else:
            os.chdir(os.path.dirname(os.path.abspath(__file__)))

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open XML File", "", "XML Files (*.xml *.txt)")
        if file_path:
            self.load_xml(file_path)

    def load_xml(self, file_path):
        try:
            self.xml_tree = ET.parse(file_path)
            self.xml_root = self.xml_tree.getroot()
            self.populate_fields()
            self.update_text_area()
            self.save_button.setEnabled(True)
        except ET.ParseError as e:
            QMessageBox.critical(self, "Error", f"Failed to parse XML file: {e}")

    def populate_fields(self):
        # Clear existing input fields
        for field in self.input_fields.values():
            for widget in field:
                widget.deleteLater()
        self.input_fields = {}

        for elem in self.xml_root.iter():
            hbox = QHBoxLayout()
            element_label = QLabel(f"Element: {elem.tag}")

            if elem == self.xml_root or elem.tag in ["title", "compbody", "thead", "tgroup", "table"]:
                continue

            # Editable elements if text is not empty
            remove_button = QPushButton("Remove Element")
            remove_button.clicked.connect(lambda _, e=elem: self.remove_element(e))
            hbox.addWidget(element_label)
            hbox.addWidget(remove_button)

            text_hbox = QHBoxLayout()

            # Check if the text is empty
            if not elem.text or not elem.text.strip():
                # text_input.setReadOnly(True)  # Make non-editable if empty
                continue
            else:                
                text_label = QLabel("Text")
                text_input = QLineEdit(elem.text if elem.text else "")
                text_input.textChanged.connect(lambda text, e=elem: self.modify_text(e, text))
                text_hbox.addWidget(text_label)
                text_hbox.addWidget(text_input)

                self.scroll_layout.addLayout(hbox)
                self.scroll_layout.addLayout(text_hbox)
                self.input_fields[elem] = [element_label, remove_button, text_label, text_input]

            for attr, value in elem.attrib.items():
                # Skip specific attributes from being displayed
                if attr in ["outputclass", "rowsep", "colsep", "cols"]:
                    continue

                attr_hbox = QHBoxLayout()
                attr_label = QLabel(attr)
                attr_input = QLineEdit(value)
                attr_input.textChanged.connect(lambda text, e=elem, a=attr: self.modify_attribute(e, a, text))
                attr_hbox.addWidget(attr_label)
                attr_hbox.addWidget(attr_input)
                self.scroll_layout.addLayout(attr_hbox)
                self.input_fields[(elem, attr)] = [attr_label, attr_input]

            # Handle tail text
            if elem.tail and elem.tail.strip():
                tail_hbox = QHBoxLayout()
                tail_label = QLabel("Tail Text")
                tail_input = QLineEdit(elem.tail)
                tail_input.textChanged.connect(lambda text, e=elem: self.modify_tail_text(e, text))
                tail_hbox.addWidget(tail_label)
                tail_hbox.addWidget(tail_input)

                self.scroll_layout.addLayout(tail_hbox)
                self.input_fields[(elem, 'tail')] = [tail_label, tail_input]

    def find_parent(self, root, child):
        for parent in root.iter():
            for elem in parent:
                if elem == child:
                    return parent
        return None

    def remove_element(self, element):
        parent = self.find_parent(self.xml_root, element)
        if parent is not None:
            parent.remove(element)
            self.populate_fields()
            self.update_text_area()

    def modify_text(self, element, text):
        element.text = text
        self.update_text_area()

    def modify_tail_text(self, element, text):
        element.tail = text
        self.update_text_area()

    def modify_attribute(self, element, attribute, value):
        element.set(attribute, value)
        self.update_text_area()

    def save_file_dialog(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save XML File", "", "XML Files (*.xml)")
        if file_path:
            self.save_xml(file_path)

    def save_xml(self, file_path):
        # Save the current state of the XML tree to the file
        self.xml_tree.write(file_path, encoding='utf-8', xml_declaration=True)
        QMessageBox.information(self, "Success", "File saved successfully")

    def update_text_area(self):
        xml_str = ET.tostring(self.xml_root, encoding='unicode')
        pretty_xml_str = minidom.parseString(xml_str).toprettyxml(indent="    ")
        self.text_area.setPlainText(pretty_xml_str)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = XMLModifier()
    window.show()
    sys.exit(app.exec_())
