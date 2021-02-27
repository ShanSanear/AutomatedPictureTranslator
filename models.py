from typing import List

from PyQt5.QtCore import QAbstractTableModel, Qt


class TableModel(QAbstractTableModel):
    def __init__(self):
        super(TableModel, self).__init__()
        self._data = []
        self._header_labels = ["en", "pl"]

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        try:
            return len(self._data[0])
        except IndexError:
            return 0

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._header_labels[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)

    def set_data(self, data: List[List[str]]):
        self._data = data
        self.layoutChanged.emit()
