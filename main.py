import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QFileDialog, QMessageBox, QHBoxLayout, QListWidgetItem
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QClipboard

class DragDropWidget(QListWidget):
    def __init__(self, parent=None):
        super(DragDropWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setSelectionMode(self.SingleSelection)
        self.setDragDropMode(QListWidget.DropOnly)
        self.setDefaultDropAction(Qt.CopyAction)
        self.file_paths = set()  # To avoid duplicates

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            # Check if at least one of the files/folders contains .py files
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.isfile(path) and path.endswith('.py'):
                    event.acceptProposedAction()
                    return
                elif os.path.isdir(path):
                    # Check if directory contains any .py files
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if file.endswith('.py'):
                                event.acceptProposedAction()
                                return
            event.ignore()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.isfile(path) and path.endswith('.py'):
                    if path not in self.file_paths:
                        self.file_paths.add(path)
                        self.addItem(path)
                elif os.path.isdir(path):
                    # Recursively add .py files from the directory
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if file.endswith('.py'):
                                file_path = os.path.join(root, file)
                                if file_path not in self.file_paths:
                                    self.file_paths.add(file_path)
                                    self.addItem(file_path)
            event.acceptProposedAction()
        else:
            event.ignore()

class MergePyFilesApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Files Merger")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        instruction = QLabel("Drag and drop .py files or folders containing .py files below:")
        layout.addWidget(instruction)

        self.dragDropList = DragDropWidget()
        layout.addWidget(self.dragDropList)

        button_layout = QHBoxLayout()

        self.mergeButton = QPushButton("Merge and Save")
        self.mergeButton.clicked.connect(self.merge_files)
        button_layout.addWidget(self.mergeButton)

        self.copyButton = QPushButton("Merge and Copy to Clipboard")
        self.copyButton.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(self.copyButton)

        # Optional: Add buttons to remove selected files or clear the list
        self.removeButton = QPushButton("Remove Selected")
        self.removeButton.clicked.connect(self.remove_selected)
        button_layout.addWidget(self.removeButton)

        self.clearButton = QPushButton("Clear List")
        self.clearButton.clicked.connect(self.clear_list)
        button_layout.addWidget(self.clearButton)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def remove_selected(self):
        selected_items = self.dragDropList.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select files to remove.")
            return
        for item in selected_items:
            path = item.text()
            self.dragDropList.file_paths.discard(path)
            self.dragDropList.takeItem(self.dragDropList.row(item))

    def clear_list(self):
        self.dragDropList.clear()
        self.dragDropList.file_paths.clear()

    def merge_files_content(self):
        if not self.dragDropList.file_paths:
            QMessageBox.warning(self, "No Files", "Please add at least one .py file or folder to merge.")
            return None

        merged_content = ""
        # Determine the common path to compute relative paths
        try:
            common_path = os.path.commonpath(list(self.dragDropList.file_paths))
        except ValueError:
            # If there's no common path, use the absolute paths
            common_path = "/"

        for file_path in sorted(self.dragDropList.file_paths):
            # Get relative path for the separator
            try:
                relative_path = os.path.relpath(file_path, common_path)
            except ValueError:
                # In case of different drives on Windows
                relative_path = file_path

            separator = f"\n\n----{relative_path}----\n\n"
            merged_content += separator
            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    merged_content += content
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read {file_path}:\n{str(e)}")
                return None
        return merged_content

    def merge_files(self):
        merged_content = self.merge_files_content()
        if merged_content is None:
            return  # An error occurred during merging

        # Ask user where to save the merged file
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog  # You can try removing this if you prefer native dialogs
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Merged File", "merged.py",
            "Python Files (*.py);;All Files (*)", options=options
        )
        if not save_path:
            return  # User cancelled

        try:
            with open(save_path, 'w', encoding='utf-8') as outfile:
                outfile.write(merged_content)
            QMessageBox.information(self, "Success", f"Files merged successfully into:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving:\n{str(e)}")

    def copy_to_clipboard(self):
        merged_content = self.merge_files_content()
        if merged_content is None:
            return  # An error occurred during merging

        clipboard = QApplication.clipboard()
        clipboard.setText(merged_content)
        QMessageBox.information(self, "Success", "Merged content has been copied to the clipboard.")

def main():
    app = QApplication(sys.argv)
    window = MergePyFilesApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
        main()
