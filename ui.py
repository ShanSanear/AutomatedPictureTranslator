from functools import partial

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton
import sys


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My title")
        self.resize(300, 300)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label_field = QLabel("This will be translated text")
        self.set_top_left = QPushButton("TOP LEFT")
        self.set_bottom_right = QPushButton("BOTTOM RIGHT")
        # self.text = QTextEdit()
        layout.addWidget(self.label_field)
        layout.addWidget(self.set_top_left)
        layout.addWidget(self.set_bottom_right)
        self.set_top_left.clicked.connect(partial(self.check_mouse_position, self.set_top_left))
        # layout.addWidget(self.text)

    def check_mouse_position(self, button):
        print("CLICK")
        print(button)


app = QApplication(sys.argv)

app.setStyleSheet("""
QLabel {
font-size: 25px;
font-style: bold;
border: 2px solid red;
}
""")
window = MyApp()
window.show()
app.exec()
