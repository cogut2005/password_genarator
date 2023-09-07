import sqlite3
import random
import string
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, 
                             QPushButton, QListWidget, QVBoxLayout, QWidget, 
                             QSpinBox, QComboBox, QMessageBox)
from PyQt5.QtCore import QFile, QTextStream

DB_PATH = 'passwords.db'

def setup_database():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        );
    ''')
    connection.commit()
    connection.close()

def generate_password(length, upper, lower, numbers, special):
    if length < (upper + lower + numbers + special):
        return None
    characters = ''.join([
        ''.join(random.choice(string.ascii_uppercase) for _ in range(upper)),
        ''.join(random.choice(string.ascii_lowercase) for _ in range(lower)),
        ''.join(random.choice(string.digits) for _ in range(numbers)),
        ''.join(random.choice(string.punctuation) for _ in range(special))
    ])
    characters = ''.join(random.sample(characters, len(characters)))
    while len(characters) < length:
        characters += random.choice(string.ascii_lowercase)
    return ''.join(random.sample(characters, len(characters)))

def load_stylesheet(filename):
    file = QFile(filename)
    if not file.exists():
        raise FileNotFoundError(f"The file {filename} does not exist.")
    if not file.open(QFile.ReadOnly | QFile.Text):
        raise IOError(f"Cannot open file {filename} for reading.")
    stream = QTextStream(file)
    return stream.readAll()

class PasswordApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setGeometry(100, 100, 400, 500)
        self.setWindowTitle("Password Generator")
        layout = QVBoxLayout()

        self.label_name = QLabel("Name/Username:")
        layout.addWidget(self.label_name)
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        self.label_length = QLabel("Password Length:")
        self.length_input = QSpinBox()
        self.length_input.setMinimum(1)
        self.length_input.setMaximum(100)
        self.length_input.setValue(12)
        layout.addWidget(self.label_length)
        layout.addWidget(self.length_input)

        self.label_upper = QLabel("Uppercase Letters:")
        self.upper_input = QSpinBox()
        layout.addWidget(self.label_upper)
        layout.addWidget(self.upper_input)

        self.label_lower = QLabel("Lowercase Letters:")
        self.lower_input = QSpinBox()
        layout.addWidget(self.label_lower)
        layout.addWidget(self.lower_input)

        self.label_numbers = QLabel("Numbers:")
        self.numbers_input = QSpinBox()
        layout.addWidget(self.label_numbers)
        layout.addWidget(self.numbers_input)

        self.label_special = QLabel("Special Characters:")
        self.special_input = QSpinBox()
        layout.addWidget(self.label_special)
        layout.addWidget(self.special_input)

        self.generate_button = QPushButton("Generate")
        self.generate_button.clicked.connect(self.generate)
        layout.addWidget(self.generate_button)

        self.label_password = QLabel("Generated Password:")
        layout.addWidget(self.label_password)

        self.password_display = QLineEdit()
        layout.addWidget(self.password_display)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save)
        layout.addWidget(self.save_button)

        self.list_label = QLabel("Saved Passwords:")
        layout.addWidget(self.list_label)
        self.password_list = QListWidget()
        layout.addWidget(self.password_list)

        self.load_button = QPushButton("Load Saved Passwords")
        self.load_button.clicked.connect(self.load_passwords)
        layout.addWidget(self.load_button)

        self.delete_button = QPushButton("Delete Selected Password")
        self.delete_button.clicked.connect(self.delete_password)
        layout.addWidget(self.delete_button)

        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["Light Theme", "Dark Theme"])
        self.theme_selector.setCurrentIndex(0)
        self.theme_selector.currentIndexChanged.connect(self.apply_theme)
        layout.addWidget(self.theme_selector)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def generate(self):
        length = self.length_input.value()
        upper = self.upper_input.value()
        lower = self.lower_input.value()
        numbers = self.numbers_input.value()
        special = self.special_input.value()

        if upper + lower + numbers + special > length:
            QMessageBox.warning(self, "Error", "The combined count of character types exceeds the password length!")
            return

        password = generate_password(length, upper, lower, numbers, special)
        self.password_display.setText(password)

    def save(self):
        name = self.name_input.text()
        password = self.password_display.text()
        if not name or not password:
            print("Name and Password cannot be empty.")
            return
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO passwords (name, password) VALUES (?, ?)", (name, password))
        connection.commit()
        connection.close()
        self.name_input.clear()
        self.password_display.clear()

    def load_passwords(self):
        self.password_list.clear()
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute("SELECT name, password FROM passwords")
        for row in cursor.fetchall():
            self.password_list.addItem(f"{row[0]}: {row[1]}")
        connection.close()

    def delete_password(self):
        current_item = self.password_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Selection Error", "Please select a password to delete.")
            return
        name = current_item.text().split(":")[0].strip()
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute("DELETE FROM passwords WHERE name=?", (name,))
        connection.commit()
        connection.close()
        row = self.password_list.row(current_item)
        self.password_list.takeItem(row)

    def apply_theme(self, index):
        if index == 0:  # Light Theme
            stylesheet = load_stylesheet('themes/light_theme.css')
        else:  # Dark Theme
            stylesheet = load_stylesheet('themes/dark_theme.css')
        app.setStyleSheet(stylesheet)

if __name__ == "__main__":
    setup_database()

    app = QApplication([])

    stylesheet = load_stylesheet('themes/light_theme.css')
    app.setStyleSheet(stylesheet)

    window = PasswordApp()
    window.show()
    app.exec_()
