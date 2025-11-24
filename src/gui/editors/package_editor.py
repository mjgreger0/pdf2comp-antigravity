from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                               QTableWidgetItem, QLabel, QHeaderView, QSplitter)
from PySide6.QtCore import Qt

class PackageEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Splitter for Table vs 3D View
        self.splitter = QSplitter(Qt.Vertical)
        
        # Dimensions Table
        self.table_container = QWidget()
        self.table_layout = QVBoxLayout(self.table_container)
        self.table_layout.setContentsMargins(0, 0, 0, 0)
        self.table_label = QLabel("IPC-7351 Dimensions")
        self.dimensions_table = QTableWidget(0, 2)
        self.dimensions_table.setHorizontalHeaderLabels(["Dimension", "Value (mm)"])
        self.dimensions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_layout.addWidget(self.table_label)
        self.table_layout.addWidget(self.dimensions_table)
        
        # 3D View Placeholder
        self.view_container = QWidget()
        self.view_layout = QVBoxLayout(self.view_container)
        self.view_layout.setContentsMargins(0, 0, 0, 0)
        self.view_label = QLabel("3D Preview (Placeholder)")
        self.view_placeholder = QLabel("3D Model View\n(PyVistaQt integration goes here)")
        self.view_placeholder.setAlignment(Qt.AlignCenter)
        self.view_placeholder.setStyleSheet("background-color: #333; color: #aaa; border: 1px solid #555;")
        self.view_layout.addWidget(self.view_label)
        self.view_layout.addWidget(self.view_placeholder)
        
        self.splitter.addWidget(self.table_container)
        self.splitter.addWidget(self.view_container)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)
        
        self.layout.addWidget(self.splitter)

    def set_dimensions(self, dimensions):
        """
        Populate dimensions table.
        :param dimensions: Dictionary of {name: value}
        """
        self.dimensions_table.setRowCount(len(dimensions))
        for i, (key, value) in enumerate(dimensions.items()):
            self.dimensions_table.setItem(i, 0, QTableWidgetItem(str(key)))
            self.dimensions_table.setItem(i, 1, QTableWidgetItem(str(value)))

    def get_dimensions(self):
        """
        Return dictionary of dimensions from table.
        """
        dims = {}
        for i in range(self.dimensions_table.rowCount()):
            key = self.dimensions_table.item(i, 0).text()
            value = self.dimensions_table.item(i, 1).text()
            dims[key] = value
        return dims
