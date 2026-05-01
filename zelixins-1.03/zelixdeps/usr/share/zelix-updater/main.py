import sys
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QPushButton, QProgressBar, QTextEdit, QLabel
)
from PyQt6.QtCore import QProcess, Qt
from PyQt6.QtGui import QFont, QColor, QTextCursor

class UpdaterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZelixOS Updater")
        self.resize(700, 500)

        # Apply a basic navy blue / dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a2530;
            }
            QLabel {
                color: #ecf0f1;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
                color: #bdc3c7;
            }
            QProgressBar {
                border: 2px solid #2c3e50;
                border-radius: 4px;
                text-align: center;
                color: white;
                background-color: #2c3e50;
            }
            QProgressBar::chunk {
                background-color: #2ecc71;
                width: 20px;
            }
            QTextEdit {
                background-color: #0d131a;
                color: #d4d4d4;
                border: 1px solid #34495e;
                border-radius: 4px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Title Label
        self.status_label = QLabel("ZelixOS System Updater")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(self.status_label)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(25)
        layout.addWidget(self.progress_bar)

        # Log View
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        font = QFont("Monospace", 10)
        font.setStyleHint(QFont.StyleHint.TypeWriter)
        self.log_view.setFont(font)
        layout.addWidget(self.log_view)

        # Update Button
        self.update_button = QPushButton("Check & Update System")
        self.update_button.setFixedHeight(40)
        self.update_button.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.update_button.clicked.connect(self.start_update)
        layout.addWidget(self.update_button)

        self.process = None

    def start_update(self):
        self.update_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_view.clear()
        self.status_label.setText("Updating system... Please wait.")
        
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)

        # Run sudo pacman -Syu --noconfirm
        self.process.start("pkexec", ["pacman", "-Syu", "--noconfirm"])

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        # Handle decoding errors gracefully
        stdout = bytes(data).decode("utf8", errors="replace")
        
        # Pacman can use carriage returns (\r) to overwrite the current line (e.g., for progress)
        for line in stdout.split('\n'):
            if not line:
                continue
            
            clean_line = line.split('\r')[-1].strip()
            if clean_line:
                self.append_log(clean_line)
                self.parse_progress(clean_line)

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8", errors="replace")
        
        for line in stderr.split('\n'):
            clean_line = line.split('\r')[-1].strip()
            if clean_line:
                # Append error in red
                self.log_view.setTextColor(QColor("red"))
                self.log_view.append(clean_line)
                self.log_view.setTextColor(QColor("#d4d4d4")) # reset color
                # Scroll to bottom
                cursor = self.log_view.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.log_view.setTextCursor(cursor)

    def append_log(self, text):
        self.log_view.append(text)
        # Auto-scroll to bottom
        cursor = self.log_view.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_view.setTextCursor(cursor)

    def parse_progress(self, text):
        # Match lines like: ( 1/100) upgrading something...
        match = re.search(r'\(\s*(\d+)/(\d+)\)', text)
        if match:
            current = int(match.group(1))
            total = int(match.group(2))
            if total > 0:
                percentage = int((current / total) * 100)
                self.progress_bar.setValue(percentage)

    def process_finished(self, exit_code, exit_status):
        self.update_button.setEnabled(True)
        self.update_button.setText("Update Finished")
        
        if exit_code == 0:
            self.status_label.setText("System update completed successfully!")
            self.progress_bar.setValue(100)
            self.status_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2ecc71; margin-bottom: 10px;")
        else:
            self.status_label.setText("Update failed! Please check logs.")
            self.status_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #e74c3c; margin-bottom: 10px;")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UpdaterWindow()
    window.show()
    sys.exit(app.exec())
