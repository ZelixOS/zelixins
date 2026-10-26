import sys
import os
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QPushButton, QProgressBar, QTextEdit, QLabel
)
from PyQt6.QtCore import QProcess, Qt
from PyQt6.QtGui import QFont, QColor, QTextCursor, QIcon

class UpdaterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZelixOS Updater")
        for icon_candidate in (
            "/usr/share/zelix/zelix-updater.png",
            "/usr/share/pixmaps/zelix-updater.png",
            "/usr/share/zelix/zelix-icon.png",
        ):
            if os.path.exists(icon_candidate):
                self.setWindowIcon(QIcon(icon_candidate))
                break
        self.resize(720, 520)

        # Monochromatic Minimalist Theme (OLED Black / Pure White)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0E0F12;
            }
            QLabel {
                color: #FFFFFF;
                font-family: 'Segoe UI', 'Noto Sans', sans-serif;
            }
            QPushButton {
                background-color: #FFFFFF;
                color: #000000;
                font-weight: bold;
                border: 1px solid #FFFFFF;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
                border: 1px solid #E0E0E0;
                color: #000000;
            }
            QPushButton:pressed {
                background-color: #CCCCCC;
            }
            QPushButton:disabled {
                background-color: #18191E;
                color: #555560;
                border: 1px solid #24252C;
            }
            QProgressBar {
                border: 1px solid #282932;
                border-radius: 6px;
                text-align: center;
                color: #FFFFFF;
                background-color: #16171B;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #FFFFFF;
                border-radius: 4px;
                margin: 1px;
            }
            QTextEdit {
                background-color: #0A0B0E;
                color: #D8D8E0;
                border: 1px solid #202126;
                border-radius: 6px;
                padding: 8px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        central_widget.setLayout(layout)

        # Title Label
        self.status_label = QLabel("ZelixOS System Updater")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 4px;")
        layout.addWidget(self.status_label)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(22)
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
        self.update_button.setFixedHeight(44)
        self.update_button.clicked.connect(self.start_update)
        layout.addWidget(self.update_button)

        self.process = None

    def start_update(self):
        self.update_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_view.clear()
        self.status_label.setText("Updating system... Please wait.")
        self.status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #FFFFFF; margin-bottom: 4px;")
        
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)

        # Run pkexec pacman -Syu --noconfirm
        self.process.start("pkexec", ["pacman", "-Syu", "--noconfirm"])

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8", errors="replace")
        
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
                self.log_view.setTextColor(QColor("#FF5555"))
                self.log_view.append(clean_line)
                self.log_view.setTextColor(QColor("#D8D8E0"))
                cursor = self.log_view.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.log_view.setTextCursor(cursor)

    def append_log(self, text):
        self.log_view.append(text)
        cursor = self.log_view.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_view.setTextCursor(cursor)

    def parse_progress(self, text):
        match = re.search(r'\(\s*(\d+)/(\d+)\)', text)
        if match:
            current = int(match.group(1))
            total = int(match.group(2))
            if total > 0:
                percentage = int((current / total) * 100)
                self.progress_bar.setValue(percentage)
                return

        pct_match = re.search(r'(\d{1,3})\s*%', text)
        if pct_match:
            pct = int(pct_match.group(1))
            if 0 <= pct <= 100:
                self.progress_bar.setValue(pct)

    def process_finished(self, exit_code, exit_status):
        self.update_button.setEnabled(True)
        
        if exit_code == 0:
            self.update_button.setText("Update Finished")
            self.status_label.setText("System update completed successfully!")
            self.progress_bar.setValue(100)
            self.status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #FFFFFF; margin-bottom: 4px;")
        elif exit_code in (126, 127):
            self.update_button.setText("Retry Update")
            self.status_label.setText("Authorization was cancelled or denied.")
            self.status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #FFAA00; margin-bottom: 4px;")
            self.append_log("[!] Update cancelled: administrator privileges were not granted.")
        else:
            self.update_button.setText("Retry Update")
            self.status_label.setText(f"Update failed (code {exit_code})! Please check logs.")
            self.status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #FF5555; margin-bottom: 4px;")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setDesktopFileName("zelix-updater")
    window = UpdaterWindow()
    window.show()
    sys.exit(app.exec())
