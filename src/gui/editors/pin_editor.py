from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QStyledItemDelegate, QComboBox, QHBoxLayout, QPushButton)
from PySide6.QtCore import Qt, Signal

PIN_TYPES = [
    "Input", "Output", "Bidirectional", "Power", "Ground", "NC", "Passive", "Clock"
]

class PinTypeDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(PIN_TYPES)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        if value in PIN_TYPES:
            editor.setCurrentText(value)

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

class PinEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Pin Table
        self.pin_table = QTableWidget(0, 4)
        self.pin_table.setHorizontalHeaderLabels(["Number", "Name", "Type", "Description"])
        self.pin_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Set Delegate for Type column (Index 2)
        self.type_delegate = PinTypeDelegate()
        self.pin_table.setItemDelegateForColumn(2, self.type_delegate)
        
        self.layout.addWidget(self.pin_table)
        
        # Buttons
        self.btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Pin")
        self.remove_btn = QPushButton("Remove Pin")
        
        self.add_btn.clicked.connect(self.add_pin)
        self.remove_btn.clicked.connect(self.remove_pin)
        
        self.btn_layout.addWidget(self.add_btn)
        self.btn_layout.addWidget(self.remove_btn)
        self.btn_layout.addStretch()
        
        self.layout.addLayout(self.btn_layout)

    def add_pin(self):
        row = self.pin_table.rowCount()
        self.pin_table.insertRow(row)
        self.pin_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        self.pin_table.setItem(row, 1, QTableWidgetItem("PinName"))
        self.pin_table.setItem(row, 2, QTableWidgetItem("Input"))
        self.pin_table.setItem(row, 3, QTableWidgetItem(""))

    def remove_pin(self):
        current_row = self.pin_table.currentRow()
        if current_row >= 0:
            self.pin_table.removeRow(current_row)

    def set_pins(self, pins):
        """
        Populate pin table.
        :param pins: List of dicts [{'number': '1', 'name': 'VCC', 'type': 'Power', 'description': '...'}]
        """
        self.pin_table.setRowCount(0)
        for pin in pins:
            row = self.pin_table.rowCount()
            self.pin_table.insertRow(row)
            self.pin_table.setItem(row, 0, QTableWidgetItem(str(pin.get('number', ''))))
            self.pin_table.setItem(row, 1, QTableWidgetItem(str(pin.get('name', ''))))
            self.pin_table.setItem(row, 2, QTableWidgetItem(str(pin.get('type', 'Input'))))
            self.pin_table.setItem(row, 3, QTableWidgetItem(str(pin.get('description', ''))))

    def get_pins(self):
        """
        Return list of pin dicts.
        """
        pins = []
        for row in range(self.pin_table.rowCount()):
            pins.append({
                'number': self.pin_table.item(row, 0).text(),
                'name': self.pin_table.item(row, 1).text(),
                'type': self.pin_table.item(row, 2).text(),
                'description': self.pin_table.item(row, 3).text()
            })
        return pins
