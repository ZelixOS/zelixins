from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QGroupBox, QMessageBox, QPlainTextEdit, QHBoxLayout)
from PyQt6.QtCore import Qt
from utils.command_runner import CommandRunner
from utils.translations import Translator

class SystemTab(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self._init_ui()
        self.runner = None
        Translator.add_listener(self)
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Header with back button
        header_layout = QHBoxLayout()
        self.btn_back = QPushButton()
        self.btn_back.setObjectName("back_btn")
        self.btn_back.clicked.connect(lambda: self.parent_window.navigate_to(0))
        header_layout.addWidget(self.btn_back)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        self.title = QLabel()
        self.title.setObjectName("title_label")
        layout.addWidget(self.title)
        
        # Updates Group
        self.update_group = QGroupBox()
        update_layout = QVBoxLayout(self.update_group)
        
        self.btn_update = QPushButton()
        self.btn_update.setObjectName("primary_btn")
        self.btn_update.clicked.connect(self.run_update)
        update_layout.addWidget(self.btn_update)
        
        layout.addWidget(self.update_group)
        
        # Maintenance Group
        self.maint_group = QGroupBox()
        maint_layout = QVBoxLayout(self.maint_group)
        
        self.btn_clear_cache = QPushButton()
        self.btn_clear_cache.clicked.connect(lambda: self.run_command(["pacman", "-Sc", "--noconfirm"]))
        
        self.btn_remove_orphans = QPushButton()
        self.btn_remove_orphans.clicked.connect(self.run_remove_orphans)
        
        maint_layout.addWidget(self.btn_clear_cache)
        maint_layout.addWidget(self.btn_remove_orphans)
        
        layout.addWidget(self.maint_group)
        
        # Terminal Output Area
        self.terminal_output = QPlainTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setStyleSheet("background-color: #000000; color: #00FF00; font-family: monospace;")
        layout.addWidget(QLabel("Terminal:"))
        layout.addWidget(self.terminal_output)
        
        self.retranslate_ui()

    def retranslate_ui(self):
        self.btn_back.setText(Translator.get("btn_back"))
        self.title.setText(Translator.get("sys_title"))
        self.update_group.setTitle(Translator.get("sys_title"))
        self.maint_group.setTitle(Translator.get("sys_title")) # could use a fixes key, but this is fine
        self.btn_update.setText(Translator.get("sys_update"))
        self.btn_clear_cache.setText(Translator.get("sys_clear_cache"))
        self.btn_remove_orphans.setText(Translator.get("sys_remove_orphans"))

    def log_output(self, text):
        self.terminal_output.appendPlainText(text)
        
    def run_update(self):
        self.terminal_output.clear()
        self.run_command(["pacman", "-Syu", "--noconfirm"])
        
    def run_remove_orphans(self):
        self.terminal_output.clear()
        command = ["bash", "-c", "pacman -Qdtq | pkexec pacman -Rns - --noconfirm"]
        self.run_command(command, use_pkexec=False)
        
    def run_command(self, cmd_list, use_pkexec=True):
        self.runner = CommandRunner(cmd_list, use_pkexec=use_pkexec)
        self.runner.output_signal.connect(self.log_output)
        self.runner.error_signal.connect(self.log_output)
        self.runner.finished_signal.connect(self.on_finished)
        self.runner.start()
        
    def on_finished(self, rc):
        if rc == 0:
            self.log_output(f"\n[{Translator.get('msg_success')}]")
            QMessageBox.information(self, Translator.get("msg_success"), Translator.get("msg_success"))
        else:
            self.log_output(f"\n[{Translator.get('msg_error')} - Code: {rc}]")
            QMessageBox.warning(self, Translator.get("msg_error"), Translator.get("msg_error"))
