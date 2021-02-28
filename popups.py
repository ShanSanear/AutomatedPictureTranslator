from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableView

from models import TableModel
from utils import ComboBoxWithLabel


class PyTesseractPopupSettings(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setSpacing(100)
        self.cb = ComboBoxWithLabel("Page segmentation mode", (str(i) for i in range(14)))
        layout.addLayout(self.cb.layout_)


class SingleWordTranslations(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Single word translations")
        self.table = QTableView()
        self.table.verticalHeader().setDefaultSectionSize(50)
        self.table.horizontalHeader().setDefaultSectionSize(150)
        self.model = TableModel()
        self.table.setModel(self.model)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.table)
