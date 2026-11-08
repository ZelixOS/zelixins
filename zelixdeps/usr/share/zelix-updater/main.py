import os
import sys

from PyQt6.QtCore import QProcess, Qt
from PyQt6.QtGui import QCloseEvent, QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QMainWindow, QMessageBox,
    QProgressBar, QPushButton, QTextEdit, QVBoxLayout, QWidget,
)


class UpdaterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZelixOS Updater")
        for path in ("/usr/share/zelix/zelix-updater.png", "/usr/share/pixmaps/zelix-updater.png"):
            if os.path.exists(path):
                self.setWindowIcon(QIcon(path))
                break
        self.resize(760, 560)
        self.setStyleSheet("""
            QMainWindow { background: #0e0f12; }
            QLabel { color: white; font-family: 'Noto Sans', sans-serif; }
            QPushButton { background: white; color: black; font-weight: bold;
                border: 1px solid white; border-radius: 6px; padding: 10px; }
            QPushButton:hover { background: #e0e0e0; }
            QPushButton:disabled { background: #18191e; color: #777780; border-color: #24252c; }
            QProgressBar { border: 1px solid #282932; border-radius: 6px;
                background: #16171b; color: white; text-align: center; }
            QProgressBar::chunk { background: white; border-radius: 4px; }
            QTextEdit { background: #0a0b0e; color: #d8d8e0; border: 1px solid #202126;
                border-radius: 6px; padding: 8px; }
        """)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        self.status_label = QLabel("Güncellemeleri kontrol edin")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(self.status_label)
        self.detail_label = QLabel("Resmî depolar ve yapılandırılmış paket depoları kontrol edilir. AUR paketleri dahil değildir.")
        self.detail_label.setWordWrap(True)
        layout.addWidget(self.detail_label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Monospace", 10))
        layout.addWidget(self.log_view)
        buttons = QHBoxLayout()
        self.check_button = QPushButton("Güncellemeleri kontrol et")
        self.check_button.clicked.connect(self.check_updates)
        self.update_button = QPushButton("Sistemi güncelle")
        self.update_button.setEnabled(False)
        self.update_button.clicked.connect(self.start_update)
        buttons.addWidget(self.check_button)
        buttons.addWidget(self.update_button)
        layout.addLayout(buttons)
        self.process = None
        self.operation = None
        self.stdout = bytearray()
        self.stderr = bytearray()
        self.packages = []

    def set_busy(self, busy):
        self.check_button.setEnabled(not busy)
        self.update_button.setEnabled(not busy and bool(self.packages))
        self.progress_bar.setRange(0, 0 if busy else 1)
        if not busy:
            self.progress_bar.setValue(0)

    def run_process(self, operation, program, args):
        self.operation = operation
        self.stdout = bytearray()
        self.stderr = bytearray()
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.read_stdout)
        self.process.readyReadStandardError.connect(self.read_stderr)
        self.process.finished.connect(self.process_finished)
        self.process.errorOccurred.connect(self.process_error)
        self.set_busy(True)
        self.process.start(program, args)

    def check_updates(self):
        self.packages = []
        self.log_view.clear()
        self.status_label.setText("Güncellemeler kontrol ediliyor…")
        self.run_process("check", "checkupdates", [])

    def start_update(self):
        answer = QMessageBox.question(
            self, "Güncellemeyi onayla",
            "Sistem paketleri güncellenecek. İşlem yönetici yetkisi gerektirir ve "
            "pacman sorularında varsayılan yanıtlar kullanılır. Devam edilsin mi?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.log_view.clear()
        self.status_label.setText("Sistem güncelleniyor…")
        self.run_process("update", "pkexec", ["pacman", "-Syu", "--noconfirm"])

    def read_stdout(self):
        data = bytes(self.process.readAllStandardOutput())
        self.stdout.extend(data)
        if self.operation == "update":
            self.append_output(data)

    def read_stderr(self):
        data = bytes(self.process.readAllStandardError())
        self.stderr.extend(data)
        if self.operation == "update":
            self.append_output(data)

    def append_output(self, data):
        cursor = self.log_view.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(data.decode("utf-8", errors="replace").replace("\r", "\n"))
        self.log_view.setTextCursor(cursor)
        self.log_view.ensureCursorVisible()

    def process_error(self, error):
        if error == QProcess.ProcessError.FailedToStart:
            self.status_label.setText("İşlem başlatılamadı.")
            if self.operation == "check":
                self.log_view.append("Güncelleme kontrolü başlatılamadı. pacman-contrib ve fakeroot paketlerinin kurulu olduğundan emin olun: sudo pacman -S pacman-contrib fakeroot")
            else:
                self.log_view.append(self.process.errorString())
            self.operation = None
            self.set_busy(False)

    def process_finished(self, code, exit_status):
        self.read_stdout()
        self.read_stderr()
        operation = self.operation
        self.operation = None
        success = exit_status == QProcess.ExitStatus.NormalExit
        if operation == "check":
            output = self.stdout.decode("utf-8", errors="replace").strip()
            error = self.stderr.decode("utf-8", errors="replace").strip()
            if success and code == 0 and output:
                self.packages = output.splitlines()
                self.log_view.setPlainText(output)
                self.status_label.setText(f"{len(self.packages)} paket güncellenebilir.")
                if error:
                    self.log_view.append("\n" + error)
            elif success and code == 2:
                self.status_label.setText("Sistem güncel görünüyor.")
                if error:
                    self.log_view.setPlainText(error)
            else:
                self.status_label.setText("Güncellemeler kontrol edilemedi.")
                self.log_view.setPlainText("\n".join(part for part in (output, error) if part) or f"Hata kodu: {code}")
        elif operation == "update":
            self.packages = []
            if success and code == 0:
                self.status_label.setText("Güncelleme tamamlandı.")
                self.log_view.append("\nBazı güncellemelerin etkinleşmesi için sistemi yeniden başlatmanız gerekebilir.")
            elif success and code in (126, 127):
                self.status_label.setText("Yetkilendirme iptal edildi veya reddedildi.")
            else:
                self.status_label.setText(f"Güncelleme başarısız oldu (kod: {code}).")
        self.set_busy(False)
        self.process.deleteLater()
        self.process = None

    def closeEvent(self, event: QCloseEvent):
        if self.operation:
            QMessageBox.information(self, "İşlem sürüyor", "Pencereyi kapatmadan önce işlemin tamamlanmasını bekleyin.")
            event.ignore()
        else:
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setDesktopFileName("zelix-updater")
    window = UpdaterWindow()
    window.show()
    sys.exit(app.exec())
