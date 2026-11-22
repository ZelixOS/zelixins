"""Read-only theme previews and a resizable image gallery."""
from pathlib import Path
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import (
    QFrame, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QToolButton, QSizePolicy,
)
from desktop_catalog import desktops_for


class PreviewDialog(QDialog):
    def __init__(self, title, paths, translate, parent=None):
        super().__init__(parent)
        self.paths = list(paths)
        self.index = 0
        self.tr_text = translate
        self.setWindowTitle(title)
        self.setMinimumSize(520, 380)
        available = self.screen().availableGeometry()
        self.resize(min(1000, available.width() - 60), min(740, available.height() - 80))
        self.setStyleSheet('QDialog { background: #11141a; } QLabel { color: #eef1f7; } QPushButton { padding: 8px 16px; }')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        header = QHBoxLayout()
        heading = QLabel(title)
        heading.setStyleSheet('font-size: 18px; font-weight: 600;')
        header.addWidget(heading, 1)
        self.counter = QLabel()
        header.addWidget(self.counter)
        layout.addLayout(header)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(0, 0)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        layout.addWidget(self.image_label, 1)
        self.filename = QLabel()
        self.filename.setStyleSheet('color: #9da8b9; font-size: 11px;')
        layout.addWidget(self.filename)
        footer = QHBoxLayout()
        self.previous = QPushButton(translate('preview_previous'))
        self.previous.clicked.connect(lambda: self.move(-1))
        self.next = QPushButton(translate('preview_next'))
        self.next.clicked.connect(lambda: self.move(1))
        close = QPushButton(translate('preview_close'))
        close.clicked.connect(self.accept)
        footer.addWidget(self.previous)
        footer.addWidget(self.next)
        footer.addStretch()
        footer.addWidget(close)
        layout.addLayout(footer)
        self.render()

    def move(self, offset):
        if self.paths:
            self.index = (self.index + offset) % len(self.paths)
        self.render()

    def render(self):
        self.previous.setEnabled(len(self.paths) > 1)
        self.next.setEnabled(len(self.paths) > 1)
        self.counter.setText(f'{self.index + 1} / {len(self.paths)}' if self.paths else '0 / 0')
        pixmap = QPixmap(str(self.paths[self.index])) if self.paths else QPixmap()
        if pixmap.isNull():
            self.image_label.setText(self.tr_text('preview_unavailable'))
            self.filename.clear()
        else:
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                                    Qt.TransformationMode.SmoothTransformation))
            self.filename.setText(self.paths[self.index].name)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self.render)


class ThemePreview(QFrame):
    def __init__(self, main_window, translate):
        super().__init__(main_window)
        self.main_window = main_window
        self.tr_text = translate
        self.asset_root = Path(__file__).resolve().parent
        self.component = 'desktop-theme'
        self.setObjectName('themePreview')
        self.setMinimumWidth(230)
        self.setStyleSheet('''
            QFrame#themePreview { background: #191b22; border: 1px solid #30333d; border-radius: 10px; }
            QLabel { border: none; background: transparent; }
            QToolButton { border: 1px solid #30333d; border-radius: 6px; background: #101217; padding: 0; }
            QToolButton:hover { border-color: #b7c2d4; }
        ''')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        self.heading = QLabel()
        self.heading.setStyleSheet('font-size: 15px; font-weight: 600;')
        layout.addWidget(self.heading)
        self.image_button = QToolButton()
        self.image_button.setFixedHeight(205)
        self.image_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.image_button.clicked.connect(self.open_dialog)
        layout.addWidget(self.image_button)
        self.caption = QLabel()
        self.caption.setWordWrap(True)
        self.caption.setStyleSheet('color: #a5afbf; font-size: 11px;')
        layout.addWidget(self.caption)
        self.enlarge = QPushButton()
        self.enlarge.setStyleSheet('font-size: 11px; padding: 6px 12px;')
        self.enlarge.clicked.connect(self.open_dialog)
        layout.addWidget(self.enlarge)
        layout.addStretch()
        self.retranslate()

    def sources(self, component=None):
        component = component or self.component
        if component == 'desktop-theme':
            selected = desktops_for(self.main_window.desktop_page.selected_desktops())
            slugs = [desktop.slug for desktop in selected] or ['kde-plasma']
            paths = [self.asset_root/'previews'/f'{slug}.png' for slug in slugs]
        elif component == 'wallpapers':
            root = self.asset_root/'zelixdeps/usr/share/wallpapers'
            default = root/'Zelix/minimalistic.png'
            paths = [default, *sorted(path for path in root.rglob('*') if path.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp') and path != default)]
        else:
            name = {'sddm-theme':'sddm', 'plymouth-theme':'plymouth', 'grub-theme':'grub'}.get(component)
            paths = [self.asset_root/'previews/themes'/f'{name}.png'] if name else []
        return [path for path in paths if path.is_file()]

    def show_component(self, component, enlarge=False):
        self.component = component
        self.retranslate()
        if enlarge:
            self.open_dialog()

    def open_dialog(self):
        dialog = PreviewDialog(self.tr_text('component_' + self.component), self.sources(), self.tr_text, self)
        dialog.exec()

    def render(self):
        paths = self.sources()
        pixmap = QPixmap(str(paths[0])) if paths else QPixmap()
        if pixmap.isNull():
            self.image_button.setIcon(QIcon())
            self.image_button.setText(self.tr_text('preview_unavailable'))
            self.enlarge.setEnabled(False)
        else:
            self.image_button.setText('')
            self.image_button.setIcon(QIcon(pixmap))
            self.image_button.setIconSize(QSize(max(1, self.image_button.width()-6), 199))
            self.enlarge.setEnabled(True)

    def retranslate(self):
        self.heading.setText(self.tr_text('component_' + self.component))
        self.caption.setText(self.tr_text('theme_preview_caption'))
        self.enlarge.setText(self.tr_text('preview_enlarge'))
        self.image_button.setToolTip(self.tr_text('preview_enlarge'))
        self.render()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self.render)
