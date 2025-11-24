import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QSplitter, QTreeWidget, QTreeWidgetItem, QTabWidget)
from PySide6.QtCore import Qt

from src.gui.pdf_viewer import PdfViewer
from src.gui.editors.component_editor import ComponentEditor
from src.gui.editors.package_editor import PackageEditor
from src.gui.editors.pin_editor import PinEditor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MinerU to KiCAD Component Generator")
        self.resize(1600, 900)

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Main Splitter (Left: Tree, Center: PDF, Right: Editors)
        self.main_splitter = QSplitter(Qt.Horizontal)
        
        # 1. Left Pane: Project Tree
        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderLabel("Project Explorer")
        self.populate_dummy_tree()  # Placeholder data
        
        # 2. Center Pane: PDF Viewer
        self.pdf_viewer = PdfViewer()
        # Load a dummy PDF if available or just leave empty
        
        # 3. Right Pane: Data Editors
        self.editor_tabs = QTabWidget()
        self.component_editor = ComponentEditor()
        self.package_editor = PackageEditor()
        self.pin_editor = PinEditor()
        
        self.editor_tabs.addTab(self.component_editor, "Component")
        self.editor_tabs.addTab(self.package_editor, "Package")
        self.editor_tabs.addTab(self.pin_editor, "Pins")
        
        # Add widgets to splitter
        self.main_splitter.addWidget(self.project_tree)
        self.main_splitter.addWidget(self.pdf_viewer)
        self.main_splitter.addWidget(self.editor_tabs)
        
        # Set initial sizes (approx 20%, 50%, 30%)
        self.main_splitter.setStretchFactor(0, 1)
        self.main_splitter.setStretchFactor(1, 3)
        self.main_splitter.setStretchFactor(2, 2)
        
        main_layout.addWidget(self.main_splitter)

    def populate_dummy_tree(self):
        root = QTreeWidgetItem(self.project_tree, ["Datasheet.pdf"])
        comp = QTreeWidgetItem(root, ["Component A"])
        QTreeWidgetItem(comp, ["Package X"])
        QTreeWidgetItem(comp, ["Pinout"])
        self.project_tree.expandAll()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
