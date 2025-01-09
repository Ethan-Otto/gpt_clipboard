def select_directory(self):
        """Handle folder selection via dialog."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            os.path.expanduser("~"),  # Start in home directory
            QFileDialog.ShowDirsOnly
        )
        
        if directory:
            self.file_list.process_directory(directory)
import sys
import os
import platform
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QFileDialog, QMessageBox, QHBoxLayout, QListWidgetItem,
    QTreeWidget, QTreeWidgetItem, QSplitter
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QClipboard, QIcon

class DirectoryTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("Project Structure")
        self.setColumnCount(1)

    def build_tree(self, root_path):
        self.clear()
        
        # Create root item
        root_item = QTreeWidgetItem(self)
        root_item.setText(0, os.path.basename(root_path))
        self.expandItem(root_item)
        
        # Build tree structure
        for root, dirs, files in os.walk(root_path):
            # Skip hidden directories except .notes
            dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.notes']
            
            # Get the path relative to the root
            rel_path = os.path.relpath(root, root_path)
            
            # Skip if this is the root directory
            if rel_path == '.':
                parent_item = root_item
            else:
                # Find or create parent item
                path_parts = rel_path.split(os.sep)
                parent_item = root_item
                for part in path_parts:
                    # Look for existing item
                    child_item = None
                    for i in range(parent_item.childCount()):
                        if parent_item.child(i).text(0) == part:
                            child_item = parent_item.child(i)
                            break
                    
                    if not child_item:
                        child_item = QTreeWidgetItem(parent_item)
                        child_item.setText(0, part)
                    parent_item = child_item
            
            # Add files
            for file in sorted(files):
                if file.endswith(('.py', '.md')):
                    file_item = QTreeWidgetItem(parent_item)
                    file_item.setText(0, file)
        
        # Expand all items
        self.expandAll()

    def get_tree_text(self):
        """Convert the tree structure to text format."""
        root_item = self.topLevelItem(0)
        if not root_item:
            return ""
        
        lines = [
            "Project Structure:",
            "================="
            "",
            root_item.text(0)  # Root directory name
        ]
        
        # Process all children of root
        child_count = root_item.childCount()
        for i in range(child_count):
            self._get_tree_text_recursive(
                root_item.child(i), 
                "", 
                lines,
                is_last=(i == child_count - 1)
            )
            
        return "\n".join(lines)

    def _get_tree_text_recursive(self, item, prefix, lines, is_last=False):
        """Recursively build text representation of the tree."""
        # Use different connector for last item
        if is_last:
            connector = "└── "
        else:
            connector = "├── "
            
        lines.append(prefix + connector + item.text(0))
        
        child_count = item.childCount()
        for i in range(child_count):
            if is_last:
                new_prefix = prefix + "    "
            else:
                new_prefix = prefix + "│   "
                
            self._get_tree_text_recursive(
                item.child(i), 
                new_prefix, 
                lines,
                is_last=(i == child_count - 1)
            )

class FileListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setSelectionMode(self.ExtendedSelection)
        self.file_paths = set()
        self.root_path = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            # Accept folder drops
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.isdir(path):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.isdir(path):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                print(f"Dropped path: {path}")  # Debug print
                if os.path.isdir(path):
                    print(f"Processing directory: {path}")  # Debug print
                    self.process_directory(path)
                    break  # Only process the first directory
            event.acceptProposedAction()
        else:
            event.ignore()

    def process_directory(self, directory_path):
        self.clear()
        self.file_paths.clear()
        self.root_path = directory_path

        # Update the parent's tree view
        if isinstance(self.parent(), MergePyFilesApp):
            self.parent().directory_tree.build_tree(directory_path)
            print(f"Building tree for: {directory_path}")  # Debug print

        # Recursively add supported files
        for root, dirs, files in os.walk(directory_path):
            # Skip hidden directories except .notes
            dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.notes']
            
            for file in files:
                # Skip hidden files unless they're in .notes directory
                if (not file.startswith('.') or '.notes' in root) and file.endswith(('.py', '.md')):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, directory_path)
                    self.file_paths.add(file_path)
                    self.addItem(relative_path)

class MergePyFilesApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Directory Files Merger")
        self.setGeometry(100, 100, 1000, 800)
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.svg')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"Icon not found at: {icon_path}")
        
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Create top section with instruction and upload button
        top_section = QHBoxLayout()
        
        instruction = QLabel("Drag and drop a directory or use the upload button:")
        top_section.addWidget(instruction)
        
        upload_button = QPushButton("Select Folder")
        upload_button.clicked.connect(self.select_directory)
        upload_button.setMinimumWidth(100)  # Make button wider
        top_section.addWidget(upload_button)
        
        # Add top section to main layout
        layout.addLayout(top_section)

        # Create a splitter for tree and list
        splitter = QSplitter(Qt.Horizontal)
        
        # Add tree widget
        self.directory_tree = DirectoryTreeWidget()
        splitter.addWidget(self.directory_tree)

        # Add file list
        self.file_list = FileListWidget(self)
        splitter.addWidget(self.file_list)

        # Set initial sizes
        splitter.setSizes([300, 700])
        layout.addWidget(splitter)

        button_layout = QHBoxLayout()

        self.mergeButton = QPushButton("Merge and Save")
        self.mergeButton.clicked.connect(self.merge_files)
        button_layout.addWidget(self.mergeButton)

        self.copyButton = QPushButton("Merge and Copy to Clipboard")
        self.copyButton.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(self.copyButton)

        self.clearButton = QPushButton("Clear")
        self.clearButton.clicked.connect(self.clear_all)
        button_layout.addWidget(self.clearButton)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def select_directory(self):
        """Handle folder selection via dialog."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            os.path.expanduser("~"),  # Start in home directory
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if directory:  # If a directory was selected (not cancelled)
            self.file_list.process_directory(directory)

    def clear_all(self):
        self.file_list.clear()
        self.file_list.file_paths.clear()
        self.directory_tree.clear()

    def merge_files_content(self):
        if not self.file_list.file_paths:
            QMessageBox.warning(self, "No Files", "Please add a directory containing .py or .md files.")
            return None

        # Start with project structure header
        merged_content = "Project Structure:\n"
        merged_content += "=================\n\n"
        
        # Add directory tree using os.walk
        root_path = self.file_list.root_path
        root_name = os.path.basename(root_path)
        merged_content += f"{root_name}\n"
        
        # Track directory structure for proper tree formatting
        prefix_stack = []
        
        for root, dirs, files in os.walk(root_path):
            # Filter out dot directories except .notes
            dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.notes']
            dirs.sort()  # Sort directories
            
            # Calculate current level and prefix
            level = root[len(root_path):].count(os.sep)
            
            # Update prefix stack
            while len(prefix_stack) > level:
                prefix_stack.pop()
                
            # Get current directory name (except for root)
            if root != root_path:
                dir_name = os.path.basename(root)
                # Skip dot directories except .notes
                if dir_name.startswith('.') and dir_name != '.notes':
                    continue
                prefix = ''.join(prefix_stack)
                merged_content += f"{prefix}├── {dir_name}\n"
            
            # Add files at current level
            prefix = ''.join(prefix_stack) + "│   "
            # Filter and sort files
            sorted_files = sorted(f for f in files if f.endswith(('.py', '.md')))
            for i, file in enumerate(sorted_files):
                is_last = (i == len(sorted_files) - 1 and not dirs)
                connector = "└── " if is_last else "├── "
                merged_content += f"{prefix}{connector}{file}\n"
            
            # Update prefix stack for next level
            prefix_stack.append("    " if level == len(prefix_stack) else "│   ")
        
        merged_content += "\n" + "=" * 50 + "\n\n"  # Separator after tree structure
        
        root_path = self.file_list.root_path

        # Add file contents
        for file_path in sorted(self.file_list.file_paths):
            relative_path = os.path.relpath(file_path, root_path)
            separator = f"\n\n----{relative_path}----\n\n"
            merged_content += separator
            
            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    merged_content += content
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read {relative_path}:\n{str(e)}")
                return None

        return merged_content

    def merge_files(self):
        merged_content = self.merge_files_content()
        if merged_content is None:
            return

        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Merged File", "merged.txt",
            "Text Files (*.txt);;All Files (*)", options=options
        )
        if not save_path:
            return

        try:
            with open(save_path, 'w', encoding='utf-8') as outfile:
                outfile.write(merged_content)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving:\n{str(e)}")

    def copy_to_clipboard(self):
        merged_content = self.merge_files_content()
        if merged_content is None:
            return

        clipboard = QApplication.clipboard()
        clipboard.setText(merged_content)

def main():
    app = QApplication(sys.argv)
    
    # Set up the application icon
    icon_path = os.path.join(os.path.dirname(__file__), 
                            'app_icon.ico' if platform.system() == 'Windows' else 'app_icon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = MergePyFilesApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()