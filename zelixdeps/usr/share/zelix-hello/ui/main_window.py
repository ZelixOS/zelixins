from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget
from PyQt6.QtCore import Qt

from tabs.dashboard_tab import DashboardTab
from tabs.apps_tab import AppsTab
from tabs.system_tab import SystemTab
from tabs.tweaks_tab import TweaksTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zelix Hello")
        self.setMinimumSize(900, 600)
        self.resize(1000, 700)
        
        self._init_ui()
        
    def _init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Initialize Tabs
        self.dashboard_tab = DashboardTab(self)
        self.apps_tab = AppsTab(self)
        self.system_tab = SystemTab(self)
        self.tweaks_tab = TweaksTab(self)
        
        # Add to stacked widget
        self.stacked_widget.addWidget(self.dashboard_tab)
        self.stacked_widget.addWidget(self.apps_tab)
        self.stacked_widget.addWidget(self.system_tab)
        self.stacked_widget.addWidget(self.tweaks_tab)
        
        self.stacked_widget.setCurrentIndex(0)

    def navigate_to(self, index):
        """Navigate to a specific tab index: 
        0: Dashboard
        1: Apps
        2: System
        3: Tweaks
        """
        self.stacked_widget.setCurrentIndex(index)
