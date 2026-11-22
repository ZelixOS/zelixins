"""Shared bottom navigation for every installer page."""
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy


class BottomNavigation(QFrame):
    def __init__(self, window, count, translate):
        super().__init__(window)
        self.window = window
        self.tr_text = translate
        self._style_state = None
        self.setObjectName('bottomNavigation')
        self.setStyleSheet('''
            QFrame#bottomNavigation { background: #0c0e12; border-top: 1px solid #292d36; }
            QLabel { background: transparent; border: none; }
        ''')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 8)
        layout.setSpacing(8)
        row = QHBoxLayout()
        row.setSpacing(10)
        logo = QLabel()
        pixmap = QPixmap(str(Path(__file__).resolve().parent/'icons/zelixos_logo.png'))
        logo.setPixmap(pixmap.scaled(23, 23, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        row.addWidget(logo)
        brand = QLabel('ZelixOS')
        brand.setStyleSheet('font-size: 15px; font-weight: 650;')
        row.addWidget(brand)
        self.current_label = QLabel()
        self.current_label.setStyleSheet('color: #a0aabb; font-size: 12px; padding-left: 12px;')
        row.addWidget(self.current_label, 1)
        self.back_btn = QPushButton()
        self.back_btn.setStyleSheet('padding: 7px 20px; font-size: 12px;')
        self.back_btn.clicked.connect(window.go_back_from_footer)
        self.next_btn = QPushButton()
        self.next_btn.setObjectName('primary_btn')
        self.next_btn.setStyleSheet('padding: 7px 20px; font-size: 12px;')
        self.next_btn.clicked.connect(window.continue_from_footer)
        row.addWidget(self.back_btn)
        row.addWidget(self.next_btn)
        layout.addLayout(row)
        steps = QHBoxLayout()
        steps.setSpacing(4)
        self.step_buttons = []
        for index in range(count):
            button = QPushButton()
            button.setFlat(True)
            button.setMinimumSize(0, 44)
            button.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda _checked=False, page=index: window.go_to_page(page))
            steps.addWidget(button, 1)
            self.step_buttons.append(button)
        layout.addLayout(steps)

    def retranslate(self):
        self.back_btn.setText(self.tr_text('back'))
        for index, button in enumerate(self.step_buttons):
            button.setText(f'{index + 1:02d}\n' + self.tr_text(f'nav_step_{index + 1}'))
            label = self.tr_text(f'step_{index + 1}')
            button.setToolTip(label)
            button.setAccessibleName(label)

    def sync(self, index, install_index, forward):
        locked = index == install_index
        self.back_btn.setEnabled(index > 0 and not locked)
        self.next_btn.setVisible(forward is not None and not locked)
        if forward is not None:
            self.next_btn.setText(forward.text())
            self.next_btn.setEnabled(forward.isEnabled())
        self.current_label.setText(f'{index + 1:02d} / {len(self.step_buttons):02d}  ·  ' + self.tr_text(f'nav_step_{index + 1}'))
        if self._style_state == (index, install_index):
            return
        self._style_state = (index, install_index)
        for step, button in enumerate(self.step_buttons):
            button.setEnabled(not locked and step != install_index)
            color = '#ffffff' if step == index else '#b0b8c6' if step < index else '#697383'
            background = '#252a35' if step == index else 'transparent'
            border = '#dce3ed' if step == index else 'transparent'
            button.setStyleSheet(f'''
                QPushButton {{ background: {background}; color: {color}; border: none;
                    border-top: 2px solid {border}; border-radius: 5px;
                    padding: 3px 0; font-size: 10px; font-weight: 500; }}
                QPushButton:hover {{ background: #1b2029; color: white; }}
                QPushButton:disabled {{ color: #444c5a; }}
            ''')
