from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGroupBox, 
                             QHBoxLayout, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from utils.command_runner import CommandRunner
from utils.translations import Translator

class TweaksTab(QWidget):
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
        
        self.subtitle = QLabel()
        self.subtitle.setObjectName("dashboard_subtitle")
        layout.addWidget(self.subtitle)
        
        # Services Group
        self.services_group = QGroupBox()
        services_layout = QVBoxLayout(self.services_group)
        
        # Bluetooth
        bt_layout = QHBoxLayout()
        self.bt_label = QLabel()
        self.btn_bt_enable = QPushButton()
        self.btn_bt_disable = QPushButton()
        
        self.btn_bt_enable.clicked.connect(lambda: self.manage_service("bluetooth", "enable --now"))
        self.btn_bt_disable.clicked.connect(lambda: self.manage_service("bluetooth", "disable --now"))
        
        bt_layout.addWidget(self.bt_label)
        bt_layout.addStretch()
        bt_layout.addWidget(self.btn_bt_enable)
        bt_layout.addWidget(self.btn_bt_disable)
        services_layout.addLayout(bt_layout)
        
        # Firewall
        fw_layout = QHBoxLayout()
        self.fw_label = QLabel()
        self.btn_fw_enable = QPushButton()
        self.btn_fw_disable = QPushButton()
        
        self.btn_fw_enable.clicked.connect(lambda: self.manage_service("ufw", "enable --now"))
        self.btn_fw_disable.clicked.connect(lambda: self.manage_service("ufw", "disable --now"))
        
        fw_layout.addWidget(self.fw_label)
        fw_layout.addStretch()
        fw_layout.addWidget(self.btn_fw_enable)
        fw_layout.addWidget(self.btn_fw_disable)
        services_layout.addLayout(fw_layout)
        
        layout.addWidget(self.services_group)
        layout.addStretch()
        
        self.retranslate_ui()

    def retranslate_ui(self):
        self.btn_back.setText(Translator.get("btn_back"))
        self.title.setText(Translator.get("tw_title"))
        self.subtitle.setText(Translator.get("tw_subtitle"))
        self.services_group.setTitle(Translator.get("tw_services"))
        
        self.bt_label.setText(Translator.get("tw_bt"))
        self.btn_bt_enable.setText(Translator.get("tw_enable"))
        self.btn_bt_disable.setText(Translator.get("tw_disable"))
        
        self.fw_label.setText(Translator.get("tw_fw"))
        self.btn_fw_enable.setText(Translator.get("tw_enable"))
        self.btn_fw_disable.setText(Translator.get("tw_disable"))

    def manage_service(self, service_name, action):
        cmd = ["systemctl", action.split()[0], action.split()[1], service_name] if len(action.split()) > 1 else ["systemctl", action, service_name]
        
        self.runner = CommandRunner(cmd, use_pkexec=True)
        self.runner.finished_signal.connect(lambda rc: self.on_service_finished(rc, service_name, action))
        self.runner.start()
        
    def on_service_finished(self, rc, service_name, action):
        if rc == 0:
            QMessageBox.information(self, Translator.get("msg_success"), Translator.get("msg_success"))
        else:
            QMessageBox.warning(self, Translator.get("msg_error"), Translator.get("msg_error"))
