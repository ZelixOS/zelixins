"""Filesystem, home layout, and partition-plan selection."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QComboBox,
                            QCheckBox, QSpinBox, QPushButton, QScrollArea,
                            QTreeWidget, QTreeWidgetItem, QMessageBox)
from disk_layout import FILESYSTEMS, OTHER_FORMATS, build_partitions, partition_device


class DiskConfigPage(QWidget):
    def __init__(self, parent, translate, scan_disks, disk_size, is_uefi):
        super().__init__(parent)
        self.main_window, self.tr_text = parent, translate
        self._scan_disks, self._disk_size, self._is_uefi = scan_disks, disk_size, is_uefi
        self._size_bytes = 0
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 20)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(scroll.Shape.NoFrame)
        scroll.setStyleSheet('QScrollArea { background: #121318; border: none; } QScrollBar:vertical { background: #121318; width: 7px; margin: 0; } QScrollBar::handle:vertical { background: #4b5668; border-radius: 3px; min-height: 28px; } QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; } QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }')
        body = QWidget()
        body.setStyleSheet('background: #121318;')
        content = QVBoxLayout(body)
        content.setContentsMargins(0, 0, 10, 0)
        content.setSpacing(12)
        self.title_label = QLabel()
        self.title_label.setStyleSheet('font-size: 28px; font-weight: bold;')
        content.addWidget(self.title_label)
        self.warn_label = QLabel()
        self.warn_label.setWordWrap(True)
        self.warn_label.setStyleSheet('color: #f0a6a6; font-size: 12px;')
        content.addWidget(self.warn_label)
        self.form = QFormLayout()
        self.form.setSpacing(10)
        self.form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.disk_select_label = QLabel()
        self.disk_combo = QComboBox()
        self.refresh_btn = QPushButton()
        disk_row = QHBoxLayout()
        disk_row.addWidget(self.disk_combo, 1)
        disk_row.addWidget(self.refresh_btn)
        self.form.addRow(self.disk_select_label, disk_row)
        self.root_fs_label = QLabel()
        self.root_fs_combo = QComboBox()
        self.home_fs_label = QLabel()
        self.home_fs_combo = QComboBox()
        for combo in (self.root_fs_combo, self.home_fs_combo):
            for filesystem in FILESYSTEMS:
                combo.addItem('Btrfs' if filesystem == 'btrfs' else filesystem.upper(), filesystem)
            combo.insertSeparator(combo.count())
            for filesystem in OTHER_FORMATS:
                combo.addItem(filesystem.upper(), filesystem)
                combo.model().item(combo.count() - 1).setEnabled(False)
        self.form.addRow(self.root_fs_label, self.root_fs_combo)
        self.separate_home_check = QCheckBox()
        self.form.addRow('', self.separate_home_check)
        self.root_size_label = QLabel()
        self.root_size_spin = QSpinBox()
        self.root_size_spin.setRange(20, 1024 * 1024)
        self.root_size_spin.setValue(50)
        self.root_size_spin.setSuffix(' GiB')
        self.root_size_spin.setStyleSheet('QSpinBox { background: #17181d; border: 1px solid #282932; border-radius: 6px; padding: 8px; font-size: 14px; }')
        self.form.addRow(self.root_size_label, self.root_size_spin)
        self.form.addRow(self.home_fs_label, self.home_fs_combo)
        self.compression_check = QCheckBox()
        self.compression_check.setChecked(True)
        self.form.addRow('', self.compression_check)
        content.addLayout(self.form)
        self.filesystem_note = QLabel()
        self.filesystem_note.setWordWrap(True)
        self.filesystem_note.setStyleSheet('color: #a5afbf; font-size: 11px;')
        content.addWidget(self.filesystem_note)
        self.layout_title = QLabel()
        self.layout_title.setStyleSheet('font-size: 13px; font-weight: 600;')
        content.addWidget(self.layout_title)
        self.partition_tree = QTreeWidget()
        self.partition_tree.setColumnCount(4)
        self.partition_tree.setRootIsDecorated(True)
        self.partition_tree.setStyleSheet('QTreeWidget { background: #191b22; border: 1px solid #30333d; border-radius: 8px; } QTreeWidget::item { height: 26px; } QHeaderView::section { background: #242933; color: #b8c4d6; padding: 7px; border: none; }')
        self.partition_tree.setMinimumHeight(170)
        content.addWidget(self.partition_tree)
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet('font-size: 12px; color: #aab7c9;')
        content.addWidget(self.status_label)
        content.addStretch()
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)
        self.scroll = scroll
        navigation = QHBoxLayout()
        self.back_btn = QPushButton()
        self.back_btn.clicked.connect(parent.prev_page)
        self.next_btn = QPushButton()
        self.next_btn.clicked.connect(parent.next_page)
        navigation.addWidget(self.back_btn)
        navigation.addStretch()
        navigation.addWidget(self.next_btn)
        outer.addLayout(navigation)
        self.refresh_btn.clicked.connect(self.refresh_disks)
        self.disk_combo.currentIndexChanged.connect(self._disk_changed)
        for checkbox in (self.separate_home_check, self.compression_check):
            checkbox.toggled.connect(self.refresh_layout)
        for combo in (self.root_fs_combo, self.home_fs_combo):
            combo.currentIndexChanged.connect(self.refresh_layout)
        self.root_size_spin.valueChanged.connect(self.refresh_layout)
        self.retranslate()
        self.refresh_disks()

    def kernel_count(self):
        system = getattr(self.main_window, 'system_page', None)
        return len(system.selected_kernels()) if system else 1

    def storage_settings(self):
        return {'root_fs': self.root_fs_combo.currentData(),
                'separate_home': self.separate_home_check.isChecked(),
                'home_fs': self.home_fs_combo.currentData(), 'root_gib': self.root_size_spin.value(),
                'compression': self.compression_check.isChecked(),
                'encrypted': False}

    def planned_partitions(self, size_bytes=None):
        settings = self.storage_settings()
        return build_partitions(self._size_bytes if size_bytes is None else size_bytes,
                                self._is_uefi(), self.kernel_count(),
                                **{key: value for key, value in settings.items() if key != 'encrypted'})

    def validate_settings(self, show_error=True):
        try:
            self.planned_partitions(self._disk_size(self.disk_combo.currentText().split(' ')[0]))
            return True
        except (ValueError, OSError) as error:
            if show_error:
                QMessageBox.warning(self, self.tr_text('disk_title'), self.tr_text(str(error)))
            return False

    def clear_secrets(self):
        """Compatibility hook; disk encryption is currently unavailable."""

    def refresh_disks(self):
        previous = self.disk_combo.currentText()
        self.disk_combo.blockSignals(True)
        self.disk_combo.clear()
        self.disk_combo.addItems(self._scan_disks())
        index = self.disk_combo.findText(previous)
        if index >= 0:
            self.disk_combo.setCurrentIndex(index)
        self.disk_combo.blockSignals(False)
        self._disk_changed()

    def _disk_changed(self, *_args):
        path = self.disk_combo.currentText().split(' ')[0]
        self._size_bytes = self._disk_size(path) if path else 0
        self.refresh_layout()

    def refresh_layout(self, *_args):
        settings = self.storage_settings()
        separate = settings['separate_home']
        self.form.setRowVisible(self.root_size_spin, separate)
        self.form.setRowVisible(self.home_fs_combo, separate)
        btrfs = settings['root_fs'] == 'btrfs' or (separate and settings['home_fs'] == 'btrfs')
        self.compression_check.setEnabled(btrfs)
        maximum = max(20, (self._size_bytes // 1024**2 - max(1024, 512*self.kernel_count()) - 2) // 1024 - 8)
        self.root_size_spin.blockSignals(True)
        self.root_size_spin.setMaximum(maximum if separate else 1024 * 1024)
        self.root_size_spin.blockSignals(False)
        self.partition_tree.clear()
        try:
            partitions = self.planned_partitions()
            disk = self.disk_combo.currentText().split(' ')[0]
            for number, part in enumerate(partitions, 1):
                item = QTreeWidgetItem(self.partition_tree, [partition_device(disk, number),
                    part['mountpoint'] or '/', part['fs_type'],
                    f"{part['size']['value'] / 1024:.1f} GiB"])
                for subvolume in part['btrfs']:
                    QTreeWidgetItem(item, [subvolume['name'], subvolume['mountpoint'], 'Btrfs', '-'])
                item.setExpanded(True)
            self.partition_tree.resizeColumnToContents(0)
            self.partition_tree.resizeColumnToContents(1)
            row_count = len(partitions) + sum(len(part['btrfs']) for part in partitions)
            self.partition_tree.setFixedHeight(max(140, 40 + row_count * 27))
            self.status_label.setText(self.tr_text('disk_layout_ready'))
            self.next_btn.setEnabled(True)
        except ValueError as error:
            self.status_label.setText(self.tr_text(str(error)))
            self.next_btn.setEnabled(False)

    def retranslate(self):
        for widget, key in ((self.title_label, 'disk_title'), (self.warn_label, 'disk_warn'),
            (self.disk_select_label, 'disk_select'), (self.refresh_btn, 'disk_refresh'),
            (self.root_fs_label, 'disk_root_fs'), (self.separate_home_check, 'disk_separate_home'),
            (self.root_size_label, 'disk_root_size'), (self.home_fs_label, 'disk_home_fs'),
            (self.compression_check, 'disk_compression'),
            (self.filesystem_note, 'disk_filesystem_note'),
            (self.layout_title, 'disk_layout_preview'),
            (self.back_btn, 'back'), (self.next_btn, 'next')):
            widget.setText(self.tr_text(key))
        for combo in (self.root_fs_combo, self.home_fs_combo):
            for index in range(combo.count()):
                filesystem = combo.itemData(index)
                if filesystem in OTHER_FORMATS:
                    combo.setItemData(index, self.tr_text('disk_format_role_' + filesystem), Qt.ItemDataRole.ToolTipRole)
        self.partition_tree.setHeaderLabels([self.tr_text(key) for key in
            ('disk_column_device', 'disk_column_mount', 'disk_column_fs', 'disk_column_size')])
        self.refresh_layout()
