from PySide6.QtWidgets import (QWidget, QFormLayout, QLineEdit, 
                               QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout)

class ComponentEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Form Layout for fields
        self.form_layout = QFormLayout()
        
        self.part_number_edit = QLineEdit()
        self.manufacturer_edit = QLineEdit()
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        self.datasheet_link_edit = QLineEdit()
        
        self.form_layout.addRow("Part Number:", self.part_number_edit)
        self.form_layout.addRow("Manufacturer:", self.manufacturer_edit)
        self.form_layout.addRow("Description:", self.description_edit)
        self.form_layout.addRow("Datasheet Link:", self.datasheet_link_edit)
        
        self.layout.addLayout(self.form_layout)
        
        # Action Buttons
        self.button_layout = QHBoxLayout()
        self.extract_btn = QPushButton("Re-extract with LLM")
        self.save_btn = QPushButton("Save Corrections")
        
        self.button_layout.addWidget(self.extract_btn)
        self.button_layout.addWidget(self.save_btn)
        self.button_layout.addStretch()
        
        self.layout.addLayout(self.button_layout)
        self.layout.addStretch()

    def set_data(self, data):
        """
        Populate fields with data dictionary.
        """
        self.part_number_edit.setText(data.get("part_number", ""))
        self.manufacturer_edit.setText(data.get("manufacturer", ""))
        self.description_edit.setText(data.get("description", ""))
        self.datasheet_link_edit.setText(data.get("datasheet_link", ""))

    def get_data(self):
        """
        Return dictionary with current field values.
        """
        return {
            "part_number": self.part_number_edit.text(),
            "manufacturer": self.manufacturer_edit.text(),
            "description": self.description_edit.toPlainText(),
            "datasheet_link": self.datasheet_link_edit.text()
        }
