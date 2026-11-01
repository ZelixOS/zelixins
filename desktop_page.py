"""Multi-desktop selection with optional, user-supplied preview images."""
from pathlib import Path
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
                            QCheckBox, QComboBox, QPushButton, QToolButton,
                            QScrollArea, QFrame, QDialog)
from desktop_catalog import DESKTOPS, GREETER_NAMES, compatible_greeters, choose_greeter, find_image


class DesktopPage(QWidget):
    def __init__(self, main_window, translate, language):
        super().__init__(main_window)
        self.main_window = main_window
        self.translate = translate
        self.language = language
        self.asset_root = Path(__file__).resolve().parent
        self.cards = {}
        self.checkboxes = {}
        self.asset_signatures = {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(12)
        self.title = QLabel()
        self.title.setStyleSheet('font-size: 27px; font-weight: bold;')
        self.subtitle = QLabel()
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet('color: #AAAAAF;')
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        self.setStyleSheet("""
            QScrollArea#desktop_scroll { background: #121318; border: none; }
            QWidget#desktop_grid { background: #121318; }
            QScrollBar:vertical { background: #121318; width: 9px; margin: 0; }
            QScrollBar::handle:vertical { background: #55565F; border-radius: 4px; min-height: 24px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
        """)
        scroll = QScrollArea()
        scroll.setObjectName('desktop_scroll')
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        content.setObjectName("desktop_grid")
        grid = QGridLayout(content)
        grid.setContentsMargins(0, 0, 8, 0)
        grid.setSpacing(14)
        for index, desktop in enumerate(DESKTOPS):
            card = QFrame()
            card.setObjectName('desktop_card')
            card.setStyleSheet('''
                QFrame#desktop_card { background: #191A20; border: 1px solid #34353D; border-radius: 9px; }
                QFrame#desktop_card[selected="true"] { border: 2px solid #FFFFFF; }
                QToolButton { background: #101115; color: #92939C; border: 1px solid #2B2C34; border-radius: 5px; }
                QToolButton:hover { border-color: #AAAAAF; }
            ''')
            body = QVBoxLayout(card)
            body.setContentsMargins(14, 14, 14, 14)
            body.setSpacing(10)
            heading = QHBoxLayout()
            checkbox = QCheckBox(desktop.name)
            checkbox.setStyleSheet('font-size: 16px; font-weight: bold;')
            checkbox.setChecked(desktop.slug == 'kde-plasma')
            checkbox.toggled.connect(self.selection_changed)
            heading.addWidget(checkbox)
            badge = QLabel(desktop.session)
            badge.setStyleSheet('color: #AAAAAF; font-size: 11px;')
            heading.addStretch()
            heading.addWidget(badge)
            body.addLayout(heading)
            preview = QToolButton()
            preview.setMinimumWidth(180)
            preview.setFixedHeight(126)
            preview.setSizePolicy(preview.sizePolicy().Policy.Expanding, preview.sizePolicy().Policy.Fixed)
            preview.clicked.connect(lambda _=False, slug=desktop.slug: self.open_image(slug, 'preview'))
            body.addWidget(preview)
            description = QLabel()
            description.setWordWrap(True)
            description.setMinimumHeight(48)
            description.setStyleSheet('color: #D7D7DC; font-size: 12px;')
            body.addWidget(description)
            greeters_label = QLabel()
            greeters_label.setWordWrap(True)
            greeters_label.setStyleSheet('color: #BBBBCA; font-size: 11px;')
            body.addWidget(greeters_label)
            appearance = QLabel()
            appearance.setWordWrap(True)
            appearance.setStyleSheet('color: #AAAAAF; font-size: 11px;')
            body.addWidget(appearance)
            wallpaper_label = QLabel()
            wallpaper_label.setStyleSheet('color: #AAAAAF; font-size: 11px;')
            body.addWidget(wallpaper_label)
            wallpaper = QToolButton()
            wallpaper.setFixedHeight(65)
            wallpaper.setSizePolicy(wallpaper.sizePolicy().Policy.Expanding, wallpaper.sizePolicy().Policy.Fixed)
            wallpaper.clicked.connect(lambda _=False, slug=desktop.slug: self.open_image(slug, 'wallpaper'))
            body.addWidget(wallpaper)
            grid.addWidget(card, index//2, index%2)
            self.checkboxes[desktop.name] = checkbox
            self.cards[desktop.slug] = dict(frame=card, preview=preview, wallpaper=wallpaper,
                                           description=description, greeters_label=greeters_label, appearance=appearance,
                                           wallpaper_label=wallpaper_label)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)
        greeter_row = QHBoxLayout()
        self.greeter_label = QLabel()
        self.greeter_combo = QComboBox()
        self.greeter_combo.setMinimumWidth(190)
        greeter_row.addWidget(self.greeter_label)
        greeter_row.addWidget(self.greeter_combo, 1)
        layout.addLayout(greeter_row)
        self.status = QLabel()
        self.status.setWordWrap(True)
        self.status.setStyleSheet('color: #B5B5BE; font-size: 12px;')
        layout.addWidget(self.status)
        navigation = QHBoxLayout()
        self.back_btn = QPushButton()
        self.back_btn.clicked.connect(main_window.prev_page)
        self.next_btn = QPushButton()
        self.next_btn.setObjectName('primary_btn')
        self.next_btn.clicked.connect(main_window.next_page)
        navigation.addWidget(self.back_btn)
        navigation.addStretch()
        navigation.addWidget(self.next_btn)
        layout.addLayout(navigation)
        self.retranslate()
        # Refresh optional files added while the installer is open, without changing selection.
        self.asset_timer = QTimer(self)
        self.asset_timer.timeout.connect(self.refresh_assets)
        self.asset_timer.start(2000)

    def selected_desktops(self):
        return [desktop.name for desktop in DESKTOPS if self.checkboxes[desktop.name].isChecked()]

    def selected_greeter(self):
        return choose_greeter(self.selected_desktops(), self.greeter_combo.currentData())

    def selection_changed(self):
        names = self.selected_desktops()
        options = compatible_greeters(names)
        previous = self.greeter_combo.currentData()
        recommended = choose_greeter(names) if options else None
        self.greeter_combo.blockSignals(True)
        self.greeter_combo.clear()
        tr = self.language() == 'tr'
        for greeter in options:
            suffix = (' — Önerilen' if tr else ' — Recommended') if greeter == recommended else ''
            self.greeter_combo.addItem(GREETER_NAMES[greeter]+suffix, greeter)
        selected = previous if previous in options else recommended
        self.greeter_combo.setCurrentIndex(self.greeter_combo.findData(selected))
        self.greeter_combo.blockSignals(False)
        self.greeter_combo.setEnabled(bool(options))
        self.next_btn.setEnabled(bool(names and options))
        for desktop in DESKTOPS:
            frame = self.cards[desktop.slug]['frame']
            frame.setProperty('selected', desktop.name in names)
            frame.style().unpolish(frame)
            frame.style().polish(frame)
        if not names:
            message = 'Devam etmek için en az bir masaüstü seçin.' if tr else 'Select at least one desktop to continue.'
        elif not options:
            message = 'Seçili masaüstleri için ortak giriş yöneticisi yok; seçimi değiştirin.' if tr else 'No common greeter is available; change the desktop selection.'
        elif previous and previous not in options:
            message = 'Önceki giriş yöneticisi yeni seçimle uyumsuzdu; ortak uygun seçenek seçildi.' if tr else 'The previous greeter does not support the new selection; a common option was selected.'
        else:
            message = (f'{len(names)} masaüstü seçili. Yalnızca tümüyle uyumlu giriş yöneticileri gösterilir.' if tr else
                       f'{len(names)} desktops selected. Only greeters supported by every selection are listed.')
        self.status.setText(message)

    def image_path(self, slug, kind):
        if kind == 'preview':
            return find_image(self.asset_root/'previews', slug)
        if slug == 'kde-plasma':
            existing = self.asset_root/'zelixdeps/usr/share/wallpapers/Zelix/minimalistic.png'
            return existing if existing.is_file() else None
        return find_image(self.asset_root/'backgrounds'/slug, 'wallpaper')

    def refresh_assets(self, force=False):
        for desktop in DESKTOPS:
            for kind in ('preview', 'wallpaper'):
                path = self.image_path(desktop.slug, kind)
                try:
                    signature = (str(path), path.stat().st_mtime_ns, path.stat().st_size) if path else None
                except OSError:
                    path, signature = None, None
                key = (desktop.slug, kind)
                if not force and key in self.asset_signatures and signature == self.asset_signatures[key]:
                    continue
                self.asset_signatures[key] = signature
                button = self.cards[desktop.slug][kind]
                pixmap = QPixmap(str(path)) if path else QPixmap()
                if pixmap.isNull():
                    tr = self.language() == 'tr'
                    text = ('Ekran görüntüsü eklenecek' if tr else 'Screenshot coming soon') if kind == 'preview' else (
                        'Varsayılan Aurora duvar kâğıdı' if tr else 'Default Aurora wallpaper')
                    button.setIcon(QIcon())
                    button.setText(text)
                    button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
                    button.setEnabled(False)
                else:
                    button.setText('')
                    button.setIcon(QIcon(pixmap))
                    button.setIconSize(QSize(280, 120 if kind == 'preview' else 60))
                    button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
                    button.setEnabled(True)
                    button.setToolTip('Büyüt / Enlarge')

    def open_image(self, slug, kind):
        path = self.image_path(slug, kind)
        pixmap = QPixmap(str(path)) if path else QPixmap()
        if pixmap.isNull():
            return
        dialog = QDialog(self)
        dialog.setWindowTitle(self.checkboxes[next(d.name for d in DESKTOPS if d.slug == slug)].text())
        layout = QVBoxLayout(dialog)
        label = QLabel()
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        available = self.screen().availableGeometry().size()
        label.setPixmap(pixmap.scaled(available.width()*3//4, available.height()*3//4,
                                    Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(label)
        dialog.exec()

    def retranslate(self):
        tr = self.language() == 'tr'
        self.title.setText('Masaüstü Ortamları' if tr else 'Desktop Environments')
        self.subtitle.setText('Bir veya daha fazla masaüstü seç. Giriş ekranında oturumlar arasında geçiş yapabilirsin.' if tr else
                              'Choose one or more desktops. Switch between installed sessions at the login screen.')
        self.greeter_label.setText(self.translate('greeter'))
        self.back_btn.setText(self.translate('back'))
        self.next_btn.setText(self.translate('next'))
        for desktop in DESKTOPS:
            card = self.cards[desktop.slug]
            card['description'].setText(desktop.description_tr if tr else desktop.description_en)
            card['greeters_label'].setText(('Giriş: ' if tr else 'Login: ') + ' · '.join(GREETER_NAMES[g] for g in desktop.greeters))
            card['appearance'].setText(desktop.appearance_tr if tr else desktop.appearance_en)
            if desktop.slug == 'kde-plasma':
                card['wallpaper_label'].setText('Mevcut otomatik Aurora duvar kâğıdı' if tr else 'Existing automatic Aurora wallpaper')
            else:
                card['wallpaper_label'].setText('ZelixOS duvar kâğıdı' if tr else 'ZelixOS wallpaper')
        self.selection_changed()
        self.refresh_assets(force=True)
