import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QFileDialog, QMessageBox, QSplitter, QTextEdit, QInputDialog
)
from PyQt5.QtCore import Qt
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import git

class XMLMerger(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XML Merger")
        self.setGeometry(100, 100, 800, 600)

        self.splitter = QSplitter(Qt.Horizontal)

        # Left panel layout
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)

        self.btn_clone = QPushButton('Clone Repository', self)
        self.btn_clone.clicked.connect(self.clone_repository)
        self.left_layout.addWidget(self.btn_clone)

        self.btn_select = QPushButton('Select XML Files', self)
        self.btn_select.clicked.connect(self.openFileDialog)
        self.btn_select.setEnabled(False)  # Initially disable the button
        self.left_layout.addWidget(self.btn_select)

        self.btn_merge = QPushButton('Merge XML Files', self)
        self.btn_merge.clicked.connect(self.mergeXMLFiles)
        self.btn_merge.setEnabled(False)  # Initially disable the button
        self.left_layout.addWidget(self.btn_merge)

        self.btn_push = QPushButton('Push Changes to Git', self)
        self.btn_push.clicked.connect(self.push_changes_to_git)
        self.btn_push.setEnabled(False)  # Initially disable the button
        self.left_layout.addWidget(self.btn_push)

        self.selected_files_text = QTextEdit(self)
        self.selected_files_text.setReadOnly(True)
        self.left_layout.addWidget(self.selected_files_text)

        self.left_panel.setFixedWidth(300)  # Set fixed width for left panel

        self.splitter.addWidget(self.left_panel)

        # Right panel (text area)
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.splitter.addWidget(self.text_area)

        self.setCentralWidget(self.splitter)

        self.selected_files = []       
        self.repo = None
        self.cloned_repo_path = None
        self.merged_file_paths = []

    def clone_repository(self):
        repo_url, ok = QInputDialog.getText(self, 'Clone Repository', 'Enter GitHub repository URL:')
        if ok and repo_url:
            repo_dir = QFileDialog.getExistingDirectory(self, 'Select Directory to Clone Into')
            if repo_dir:
                self.cloned_repo_path = os.path.join(repo_dir, 'cloned_repo')
                try:
                    self.repo = git.Repo.clone_from(repo_url, self.cloned_repo_path)
                    QMessageBox.information(self, 'Success', 'Repository cloned successfully')

                    # Enable the buttons after cloning
                    self.btn_select.setEnabled(True)
                    self.btn_merge.setEnabled(True)
                except git.GitError as e:
                    QMessageBox.critical(self, 'Error', f'Failed to clone repository: {e}')

    def openFileDialog(self):
        options = QFileDialog.Options()
        initial_path = self.cloned_repo_path if self.cloned_repo_path else ""
        files, _ = QFileDialog.getOpenFileNames(self, "Select XML Files", initial_path, "XML Files (*.xml *.txt);;All Files (*)", options=options)
        if files:
            self.selected_files = files
            self.selected_files_text.setPlainText('\n'.join(files))

    def mergeXMLFiles(self):
        if not self.selected_files or len(self.selected_files) < 2:
            QMessageBox.warning(self, 'No Files Selected', 'Please select at least two XML files to merge.')
            return

        try:
            # Prompt the user to enter the file name
            file_name, ok = QInputDialog.getText(self, 'Save Merged File', 'Enter the file name for the merged XML file:')
            if not ok or not file_name.strip():
                QMessageBox.warning(self, 'Invalid File Name', 'You must enter a valid file name.')
                return

            # Ensure the file name has the correct extension
            if not file_name.endswith('.xml'):
                file_name += '.xml'

            # Merge XML files without a new root element
            merged_file_path = os.path.join(self.cloned_repo_path, 'Completed Objects', file_name)
            os.makedirs(os.path.dirname(merged_file_path), exist_ok=True)  # Ensure the directory exists

            self.merge_xml_files_without_root(self.selected_files, merged_file_path)
            self.merged_file_paths.append(merged_file_path)  # Track the merged file

            # Update the text area with the merged XML content
            with open(merged_file_path, 'r', encoding='utf-8') as f:
                merged_content = f.read()
            self.text_area.setPlainText(merged_content)

            # Enable the push button after merging
            self.btn_push.setEnabled(True)

            QMessageBox.information(self, 'Success', 'XML files merged successfully!')

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')

    def merge_xml_files_without_root(self, file_paths, output_path):
        with open(output_path, 'w', encoding='utf-8') as output_file:
            # Write the XML declaration to the output file
            output_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            
            for file_path in file_paths:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content.startswith('<?xml'):
                        content = content[content.find('?>') + 2:].strip()
                    output_file.write(content + '\n')

    def push_changes_to_git(self):
        if not self.merged_file_paths:
            QMessageBox.warning(self, 'No Merged File', 'There are no merged files to push.')
            return

        try:
            for file_path in self.merged_file_paths:
                self.repo.git.add(file_path)
            self.repo.index.commit("Merged XML files")
            origin = self.repo.remote(name='origin')
            origin.push()
            QMessageBox.information(self, 'Success', 'Changes pushed to the remote repository successfully')
        except git.GitError as e:
            QMessageBox.critical(self, 'Error', f'Failed to push changes: {e}')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = XMLMerger()
    window.show()
    sys.exit(app.exec_())
