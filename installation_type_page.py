"""Installation profile cards and independent appearance choices."""
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QPushButton, QRadioButton, QButtonGroup, QCheckBox, QBoxLayout,
)
from desktop_catalog import compatible_greeters
from theme_preview import ThemePreview
from install_profiles import PROFILES, COMPONENTS, preset, effective_components


class ProfileCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('profileCard')
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.radio = QRadioButton(self)
        self.description = QLabel(self)
        self.description.setObjectName('cardDescription')
        self.description.setWordWrap(True)
        self.description.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(5)
        layout.addWidget(self.radio)
        layout.addWidget(self.description)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.rect().contains(event.position().toPoint()):
            self.radio.click()
        super().mouseReleaseEvent(event)


class InstallationTypePage(QWidget):
    def __init__(self, main_window, translate):
        super().__init__(main_window)
        self.main_window = main_window
        self.tr_text = translate
        self._profile = 'standard'
        self._applying_profile = False
        self.setObjectName('installationTypePage')
        self.setStyleSheet('''
            QWidget#installationTypePage { background: #121318; }
            QScrollArea#profileScroll { border: none; background: transparent; }
            QWidget#profileBody { background: #121318; }
            QFrame#profileCard { background: #191b22; border: 1px solid #30333d; border-radius: 10px; }
            QFrame#profileCard:hover { background: #1e212a; border-color: #636b79; }
            QFrame#profileCard[selected="true"] { background: #242832; border: 1px solid #d4d9e3; }
            QFrame#profileCard QRadioButton { font-size: 15px; font-weight: 600; background: transparent; spacing: 9px; }
            QRadioButton::indicator { width: 14px; height: 14px; border: 1px solid #777f8e; border-radius: 8px; background: #121318; }
            QRadioButton::indicator:checked { background: #eef1f7; border: 3px solid #616a7b; }
            QLabel#cardDescription { color: #aeb5c2; font-size: 12px; border: none; background: transparent; }
            QFrame#appearancePanel { background: #191b22; border: 1px solid #30333d; border-radius: 10px; }
            QFrame#appearanceRow { border: none; background: transparent; }
            QCheckBox { background: transparent; spacing: 10px; font-size: 13px; font-weight: 500; }
            QCheckBox::indicator { width: 15px; height: 15px; border-radius: 4px; border: 1px solid #606a7b; background: #101217; }
            QCheckBox::indicator:checked { background: #e1e7f0; border: 1px solid #e1e7f0; image: url(CHECK_ICON); }
            QCheckBox::indicator:disabled { border-color: #393e49; background: #181b21; }
            QLabel#componentHint { color: #929cab; font-size: 11px; border: none; background: transparent; }
            QLabel#selectionDetail { color: #b8c0ce; font-size: 12px; }
            QLabel#sectionCaption { color: #a5afbf; font-size: 11px; font-weight: 600; letter-spacing: 1px; }
            QScrollBar:vertical { background: transparent; width: 6px; margin: 0; }
            QScrollBar::handle:vertical { background: #454d5c; border-radius: 3px; min-height: 32px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
        '''.replace('CHECK_ICON', (Path(__file__).resolve().parent / 'icons/selection-check.svg').as_posix()))
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 24, 20)
        outer.setSpacing(12)
        scroll = QScrollArea()
        scroll.setObjectName('profileScroll')
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        body = QWidget()
        body.setObjectName('profileBody')
        content = QVBoxLayout(body)
        content.setContentsMargins(0, 0, 8, 0)
        content.setSpacing(14)
        self.title_label = QLabel()
        self.title_label.setStyleSheet('font-size: 28px; font-weight: 650;')
        self.subtitle = QLabel()
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet('color: #a7afbd; font-size: 12px;')
        heading = QVBoxLayout()
        heading.setSpacing(5)
        heading.addWidget(self.title_label)
        heading.addWidget(self.subtitle)
        content.addLayout(heading)
        self.profile_cards = {}
        self.profile_group = QButtonGroup(self)
        self.profile_group.setExclusive(True)
        self.profile_grid = QGridLayout()
        grid = self.profile_grid
        grid.setSpacing(10)
        for index, name in enumerate(PROFILES):
            card = ProfileCard()
            self.profile_group.addButton(card.radio, index)
            card.radio.clicked.connect(lambda _checked=False, profile=name: self.set_profile(profile))
            self.profile_cards[name] = card
            grid.addWidget(card, index // 2, index % 2)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        content.addLayout(grid)
        self.profile_description = QLabel()
        self.profile_description.setObjectName('selectionDetail')
        self.profile_description.setWordWrap(True)
        content.addWidget(self.profile_description)
        self.appearance_heading = QLabel()
        self.appearance_heading.setObjectName('sectionCaption')
        content.addWidget(self.appearance_heading)
        panel = QFrame()
        panel.setObjectName('appearancePanel')
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(14, 5, 14, 5)
        panel_layout.setSpacing(0)
        self.preview_buttons = {}
        self.component_items = {}
        self.component_hints = {}
        for index, name in enumerate(COMPONENTS):
            if index:
                line = QFrame()
                line.setFixedHeight(1)
                line.setStyleSheet('background: #2a2e38; border: none;')
                panel_layout.addWidget(line)
            row = QFrame()
            row.setObjectName('appearanceRow')
            row_layout = QVBoxLayout(row)
            row_layout.setContentsMargins(0, 9, 0, 9)
            row_layout.setSpacing(3)
            checkbox = QCheckBox()
            hint = QLabel()
            hint.setObjectName('componentHint')
            hint.setWordWrap(True)
            hint.setContentsMargins(25, 0, 0, 0)
            checkbox.toggled.connect(lambda checked, component=name: self._component_changed(component, checked))
            heading = QHBoxLayout()
            heading.addWidget(checkbox, 1)
            preview = QPushButton()
            preview.setObjectName('previewAction')
            preview.setStyleSheet('background: transparent; color: #bac7dc; border: none; font-size: 11px; padding: 3px 8px;')
            preview.clicked.connect(lambda _checked=False, component=name: self.preview.show_component(component, enlarge=True))
            self.preview_buttons[name] = preview
            heading.addWidget(preview)
            row_layout.addLayout(heading)
            row_layout.addWidget(hint)
            panel_layout.addWidget(row)
            self.component_items[name] = checkbox
            self.component_hints[name] = hint
        self.appearance_layout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.appearance_layout.setSpacing(14)
        self.appearance_layout.addWidget(panel, 1)
        self.preview = ThemePreview(main_window, translate)
        self.appearance_layout.addWidget(self.preview, 1)
        content.addLayout(self.appearance_layout)
        content.addStretch()
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)
        self.scroll = scroll
        navigation = QHBoxLayout()
        self.back_btn = QPushButton()
        self.back_btn.clicked.connect(main_window.prev_page)
        self.next_btn = QPushButton()
        self.next_btn.setObjectName('primary_btn')
        self.next_btn.clicked.connect(main_window.next_page)
        navigation.addWidget(self.back_btn)
        navigation.addStretch()
        navigation.addWidget(self.next_btn)
        outer.addLayout(navigation)
        main_window.system_page.bootloader_combo.currentIndexChanged.connect(self.refresh_compatibility)
        main_window.desktop_page.greeter_combo.currentIndexChanged.connect(self.refresh_compatibility)
        for checkbox in main_window.desktop_page.checkboxes.values():
            checkbox.toggled.connect(self.refresh_compatibility)
        self.set_profile('standard')
        self.retranslate()

    def installation_profile(self):
        return self._profile

    def set_profile(self, name):
        if name not in PROFILES:
            raise ValueError('Unknown installation profile: ' + name)
        self._profile = name
        if name == 'custom':
            self._profile_description()
            return
        apps, components = preset(name)
        self._applying_profile = True
        try:
            self.main_window.extra_page.apply_profile_packages(apps)
            try:
                greeter = self.main_window.desktop_page.selected_greeter()
            except ValueError:
                greeter = None
            bootloader = self.main_window.system_page.selected_bootloader()
            components = effective_components(components, greeter, bootloader)
            for component, checkbox in self.component_items.items():
                checkbox.blockSignals(True)
                checkbox.setChecked(component in components)
                checkbox.blockSignals(False)
            self.refresh_compatibility()
        finally:
            self._applying_profile = False
        self._profile_description()

    def mark_custom(self, *_args):
        if not self._applying_profile:
            self._profile = 'custom'
            self._profile_description()

    def _component_changed(self, name, checked):
        if self._applying_profile:
            return
        if checked and name == 'grub-theme':
            system = self.main_window.system_page
            index = next(i for i, (_, key) in enumerate(system.BOOTLOADERS) if key == 'Grub')
            system.bootloader_combo.setCurrentIndex(index)
        elif checked and name == 'sddm-theme':
            desktop = self.main_window.desktop_page
            index = desktop.greeter_combo.findData('sddm')
            if index >= 0:
                desktop.greeter_combo.setCurrentIndex(index)
        self.mark_custom()
        self.refresh_compatibility()

    def _profile_description(self):
        for name, card in self.profile_cards.items():
            selected = name == self._profile
            card.radio.blockSignals(True)
            card.radio.setChecked(selected)
            card.radio.blockSignals(False)
            card.setProperty('selected', selected)
            card.style().unpolish(card)
            card.style().polish(card)
        applications = len(self.main_window.extra_page.get_selected_packages())
        components = sum(box.isChecked() for box in self.component_items.values())
        self.profile_description.setText(self.tr_text('profile_selection_detail').format(applications=applications, components=components))
        self.profile_description.setToolTip(self.tr_text('profile_' + self._profile + '_desc'))

    def refresh_compatibility(self, *_args):
        desktop = self.main_window.desktop_page
        try:
            greeter = desktop.selected_greeter()
        except ValueError:
            greeter = None
        bootloader = self.main_window.system_page.selected_bootloader()
        allowed = compatible_greeters(desktop.selected_desktops())
        for name, active, available in (
            ('grub-theme', bootloader == 'Grub', True),
            ('sddm-theme', greeter == 'sddm', 'sddm' in allowed),
        ):
            box = self.component_items[name]
            box.blockSignals(True)
            box.setEnabled(available)
            if not active:
                box.setChecked(False)
            elif self._profile in ('standard', 'full'):
                box.setChecked(True)
            box.blockSignals(False)
        self.preview.render()
        self.component_hints['grub-theme'].setText(self.tr_text('theme_grub_active' if bootloader == 'Grub' else 'theme_grub_switch'))
        self.component_hints['sddm-theme'].setText(self.tr_text(
            'theme_sddm_active' if greeter == 'sddm' else 'theme_sddm_switch' if 'sddm' in allowed else 'theme_sddm_unavailable'))
        self._profile_description()

    def get_selected_components(self):
        selected = [name for name, box in self.component_items.items() if box.isChecked()]
        greeter = self.main_window.desktop_page.selected_greeter()
        bootloader = self.main_window.system_page.selected_bootloader()
        return list(effective_components(selected, greeter, bootloader))

    def get_selected_component_names(self):
        return [self.tr_text('component_' + name) for name in self.get_selected_components()]

    def retranslate(self):
        self.title_label.setText(self.tr_text('installation_type_title'))
        self.subtitle.setText(self.tr_text('profile_page_intro'))
        for name, card in self.profile_cards.items():
            card.radio.setText(self.tr_text('profile_' + name))
            card.description.setText(self.tr_text('profile_card_' + name))
        self.appearance_heading.setText(self.tr_text('profile_appearance_heading'))
        for name, box in self.component_items.items():
            self.preview_buttons[name].setText(self.tr_text('preview_action'))
            box.setText(self.tr_text('component_' + name))
            box.setToolTip(self.tr_text('component_' + name + '_desc'))
            self.component_hints[name].setText(self.tr_text('component_' + name + '_desc'))
        self.preview.retranslate()
        self.refresh_compatibility()
        self.back_btn.setText(self.tr_text('back'))
        self.next_btn.setText(self.tr_text('next'))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        columns = 4 if self.width() >= 940 else 2
        for index, name in enumerate(PROFILES):
            self.profile_grid.addWidget(self.profile_cards[name], index // columns, index % columns)
        for column in range(4):
            self.profile_grid.setColumnStretch(column, 1 if column < columns else 0)
        self.appearance_layout.setDirection(QBoxLayout.Direction.LeftToRight if self.width() >= 940 else QBoxLayout.Direction.TopToBottom)
