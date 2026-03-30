from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from ui.pages.accounts_page import AccountsPage
from ui.pages.settings_page import SettingsPage
from ui.pages.dashboard_page import DashboardPage
from ui.pages.labels_page import LabelsPage
from ui.pages.printers_page import PrintersPage
from ui.pages.sales_page import SalesPage
from ui.theme import PIXEL_COLORS


class TitleBar(QFrame):
    def __init__(self, parent_window):
        super().__init__()

        self.parent_window = parent_window
        self.drag_position = QPoint()

        self.setObjectName("titleBar")
        self.setFixedHeight(42)

        layout = QHBoxLayout()
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)
        self.setLayout(layout)

        self.title_label = QLabel("SOFTWARE ML")
        self.title_label.setObjectName("titleBarLabel")

        layout.addWidget(self.title_label)
        layout.addStretch()

        self.min_button = QPushButton("—")
        self.min_button.setObjectName("titleBarButton")
        self.min_button.setFixedSize(34, 28)
        self.min_button.clicked.connect(self.parent_window.showMinimized)

        self.max_button = QPushButton("□")
        self.max_button.setObjectName("titleBarButton")
        self.max_button.setFixedSize(34, 28)
        self.max_button.clicked.connect(self._toggle_max_restore)

        self.close_button = QPushButton("✕")
        self.close_button.setObjectName("closeButton")
        self.close_button.setFixedSize(34, 28)
        self.close_button.clicked.connect(self.parent_window.close)

        layout.addWidget(self.min_button)
        layout.addWidget(self.max_button)
        layout.addWidget(self.close_button)

    def _toggle_max_restore(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
        else:
            self.parent_window.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint()
                - self.parent_window.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and not self.parent_window.isMaximized():
            self.parent_window.move(
                event.globalPosition().toPoint() - self.drag_position
            )
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._toggle_max_restore()
            event.accept()


class MainWindow(QMainWindow):
    sync_requested = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("SOFTWARE ML")
        self.setMinimumSize(1280, 800)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        self._setup_statusbar()

        root = QWidget()
        root.setObjectName("rootWindow")
        self.setCentralWidget(root)

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root.setLayout(root_layout)

        self.title_bar = TitleBar(self)
        root_layout.addWidget(self.title_bar)

        content_wrapper = QWidget()
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_wrapper.setLayout(content_layout)

        self.sidebar = self._create_sidebar()
        self.content_area = self._create_content_area()

        content_layout.addWidget(self.sidebar)
        content_layout.addWidget(self.content_area)

        root_layout.addWidget(content_wrapper)

    def _setup_statusbar(self):
        status = QStatusBar()
        status.showMessage("Sistema iniciado com sucesso.")
        self.setStatusBar(status)

    def _create_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)
        sidebar.setLayout(layout)

        brand_box = QFrame()
        brand_box.setObjectName("brandBox")

        brand_layout = QVBoxLayout()
        brand_layout.setContentsMargins(14, 14, 14, 14)
        brand_layout.setSpacing(6)
        brand_box.setLayout(brand_layout)

        pixel_badge = QLabel("◆ PIXEL PANEL")
        pixel_badge.setObjectName("pixelBadge")

        title = QLabel("SOFTWARE ML")
        title.setObjectName("appTitle")

        subtitle = QLabel("Painel de automação")
        subtitle.setObjectName("appSubtitle")

        brand_layout.addWidget(pixel_badge)
        brand_layout.addWidget(title)
        brand_layout.addWidget(subtitle)

        menu_label = QLabel("NAVEGAÇÃO")
        menu_label.setObjectName("sectionLabel")

        self.menu_list = QListWidget()
        self.menu_list.setObjectName("menuList")
        self.menu_list.setSpacing(8)
        self.menu_list.setFrameShape(QFrame.NoFrame)
        self.menu_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)

        menu_items = [
            "Dashboard",
            "Contas",
            "Vendas",
            "Etiquetas",
            "Impressoras",
            "Configurações",
            "Logs",
        ]

        for item_text in menu_items:
            item = QListWidgetItem(item_text)
            self.menu_list.addItem(item)

        self.menu_list.setCurrentRow(0)
        self.menu_list.currentRowChanged.connect(self._change_page)

        sync_button = QPushButton("Sincronizar agora")
        sync_button.setObjectName("primaryButton")
        sync_button.clicked.connect(self._on_refresh_clicked)

        footer_box = QFrame()
        footer_box.setObjectName("sidebarFooter")

        footer_layout = QVBoxLayout()
        footer_layout.setContentsMargins(12, 12, 12, 12)
        footer_layout.setSpacing(4)
        footer_box.setLayout(footer_layout)

        footer_title = QLabel("STATUS")
        footer_title.setObjectName("sectionLabel")

        footer_text = QLabel("Sistema pronto para futuras integrações.")
        footer_text.setObjectName("footerText")
        footer_text.setWordWrap(True)

        footer_layout.addWidget(footer_title)
        footer_layout.addWidget(footer_text)

        layout.addWidget(brand_box)
        layout.addSpacing(4)
        layout.addWidget(menu_label)
        layout.addWidget(self.menu_list)
        layout.addWidget(sync_button)
        layout.addStretch()
        layout.addWidget(footer_box)

        return sidebar

    def _create_content_area(self):
        container = QFrame()
        container.setObjectName("contentContainer")

        layout = QVBoxLayout()
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(0)
        container.setLayout(layout)

        self.stack = QStackedWidget()
        self.stack.setObjectName("contentStack")
        self.stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.dashboard_page = DashboardPage()
        self.accounts_page = AccountsPage()
        self.sales_page = SalesPage()
        self.labels_page = LabelsPage()
        self.printers_page = PrintersPage()
        self.settings_page = SettingsPage()

        self.stack.addWidget(self._wrap_page_in_scroll(self.dashboard_page))
        self.stack.addWidget(self._wrap_page_in_scroll(self.accounts_page))
        self.stack.addWidget(self._wrap_page_in_scroll(self.sales_page))
        self.stack.addWidget(self._wrap_page_in_scroll(self.labels_page))
        self.stack.addWidget(self._wrap_page_in_scroll(self.printers_page))
        self.stack.addWidget(self._wrap_page_in_scroll(self.settings_page))
        
        self.stack.addWidget(
            self._wrap_page_in_scroll(
                self._build_page(
                    "Logs",
                    "Acompanhe eventos, erros e ações internas.",
                )
            )
        )

        layout.addWidget(self.stack)

        return container

    def _build_page(self, title_text, description_text):
        wrapper = QWidget()

        wrapper_layout = QVBoxLayout()
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)
        wrapper.setLayout(wrapper_layout)

        page = QFrame()
        page.setObjectName("pageCard")

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        page.setLayout(layout)

        title = QLabel(title_text)
        title.setObjectName("cardTitle")

        description = QLabel(description_text)
        description.setWordWrap(True)
        description.setObjectName("cardDescription")

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addStretch()

        wrapper_layout.addWidget(page)

        return wrapper

    def _wrap_page_in_scroll(self, page_widget):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(page_widget)

        return scroll

    def _change_page(self, index):
        self.stack.setCurrentIndex(index)

        page_names = [
            "Dashboard",
            "Contas",
            "Vendas",
            "Etiquetas",
            "Impressoras",
            "Configurações",
            "Logs",
        ]

        if 0 <= index < len(page_names):
            self.statusBar().showMessage(f"Página atual: {page_names[index]}")

    def _on_refresh_clicked(self):
        current_row = self.menu_list.currentRow()

        page_names = [
            "Dashboard",
            "Contas",
            "Vendas",
            "Etiquetas",
            "Impressoras",
            "Configurações",
            "Logs",
        ]

        current_page = (
            page_names[current_row]
            if 0 <= current_row < len(page_names)
            else "Desconhecida"
        )

        self.statusBar().showMessage(
            f"Iniciando sincronização/OAuth a partir da página: {current_page}"
        )
        self.sync_requested.emit()

    def refresh_accounts_page(self):
        if hasattr(self, "accounts_page") and self.accounts_page is not None:
            self.accounts_page.load_accounts()

    def refresh_dashboard_page(self):
        if hasattr(self, "dashboard_page") and self.dashboard_page is not None:
            self.dashboard_page.refresh_monitor_status()
            self.dashboard_page.refresh_logs()

    def refresh_sales_page(self):
        if hasattr(self, "sales_page") and self.sales_page is not None:
            self.sales_page.load_orders()

    def refresh_labels_page(self):
        if hasattr(self, "labels_page") and self.labels_page is not None:
            self.labels_page.load_labels()

    def refresh_printers_page(self):
        if hasattr(self, "printers_page") and self.printers_page is not None:
            self.printers_page.load_printers()

    def _apply_styles(self):
        self.setStyleSheet(
            f"""
            QMainWindow {{
                background-color: {PIXEL_COLORS["bg_main"]};
                border: 2px solid {PIXEL_COLORS["border"]};
            }}

            QWidget {{
                color: {PIXEL_COLORS["text_main"]};
                background-color: transparent;
            }}

            #rootWindow {{
                background-color: {PIXEL_COLORS["bg_main"]};
            }}

            #titleBar {{
                background-color: {PIXEL_COLORS["bg_sidebar"]};
                border-bottom: 2px solid {PIXEL_COLORS["border"]};
            }}

            #titleBarLabel {{
                color: {PIXEL_COLORS["text_main"]};
                font-size: 13px;
                font-weight: 700;
            }}

            #titleBarButton {{
                background-color: {PIXEL_COLORS["bg_card_soft"]};
                color: {PIXEL_COLORS["text_main"]};
                border: 1px solid {PIXEL_COLORS["border"]};
                border-radius: 4px;
                font-size: 12px;
                font-weight: 700;
            }}

            #titleBarButton:hover {{
                background-color: {PIXEL_COLORS["primary"]};
            }}

            #closeButton {{
                background-color: {PIXEL_COLORS["bg_card_soft"]};
                color: {PIXEL_COLORS["text_main"]};
                border: 1px solid {PIXEL_COLORS["border"]};
                border-radius: 4px;
                font-size: 12px;
                font-weight: 700;
            }}

            #closeButton:hover {{
                background-color: #8b2d3b;
            }}

            #sidebar {{
                background-color: {PIXEL_COLORS["bg_sidebar"]};
                border-right: 2px solid {PIXEL_COLORS["border"]};
            }}

            #brandBox {{
                background-color: {PIXEL_COLORS["bg_card"]};
                border: 2px solid {PIXEL_COLORS["border"]};
                border-radius: 8px;
            }}

            #pixelBadge {{
                color: {PIXEL_COLORS["accent"]};
                font-size: 12px;
                font-weight: 700;
            }}

            #appTitle {{
                color: {PIXEL_COLORS["text_main"]};
                font-size: 26px;
                font-weight: 800;
            }}

            #appSubtitle {{
                color: {PIXEL_COLORS["text_soft"]};
                font-size: 13px;
            }}

            #sectionLabel {{
                color: {PIXEL_COLORS["primary"]};
                font-size: 12px;
                font-weight: 800;
            }}

            #menuList {{
                background-color: transparent;
                border: none;
                outline: none;
                padding: 0px;
            }}

            #menuList::item {{
                background-color: {PIXEL_COLORS["bg_card"]};
                color: {PIXEL_COLORS["text_main"]};
                border: 1px solid {PIXEL_COLORS["border"]};
                border-radius: 8px;
                padding: 16px 14px;
                margin: 0px 0px 6px 0px;
            }}

            #menuList::item:selected {{
                background-color: {PIXEL_COLORS["primary"]};
                color: {PIXEL_COLORS["text_main"]};
                border: 1px solid {PIXEL_COLORS["accent"]};
            }}

            #menuList::item:hover {{
                background-color: {PIXEL_COLORS["bg_card_soft"]};
            }}

            #primaryButton {{
                background-color: {PIXEL_COLORS["primary"]};
                color: {PIXEL_COLORS["text_main"]};
                border: 2px solid {PIXEL_COLORS["border"]};
                border-radius: 6px;
                padding: 12px 16px;
                font-size: 13px;
                font-weight: 800;
            }}

            #primaryButton:hover {{
                background-color: {PIXEL_COLORS["accent"]};
                color: {PIXEL_COLORS["bg_main"]};
            }}

            #contentContainer {{
                background-color: {PIXEL_COLORS["bg_main"]};
            }}

            #pageCard,
            #dashboardCard,
            #activityPanel,
            #infoPanel {{
                background-color: {PIXEL_COLORS["bg_card"]};
                border: 2px solid {PIXEL_COLORS["border"]};
                border-radius: 10px;
            }}

            #pageTitle,
            #panelTitle,
            #cardTitle {{
                color: {PIXEL_COLORS["text_main"]};
                font-size: 18px;
                font-weight: 800;
            }}

            #cardValue {{
                color: {PIXEL_COLORS["text_main"]};
                font-size: 26px;
                font-weight: 800;
            }}

            #cardDescription,
            #panelText,
            #footerText,
            #cardHint,
            #pageSubtitle {{
                color: {PIXEL_COLORS["text_soft"]};
                font-size: 13px;
            }}

            #cardTitleSmall {{
                color: {PIXEL_COLORS["text_main"]};
                font-size: 14px;
                font-weight: 700;
            }}

            #cardTopBar {{
                background-color: {PIXEL_COLORS["primary"]};
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}

            #sidebarFooter {{
                background-color: {PIXEL_COLORS["bg_card"]};
                border: 1px solid {PIXEL_COLORS["border"]};
                border-radius: 8px;
            }}

            QStatusBar {{
                background-color: {PIXEL_COLORS["bg_sidebar"]};
                color: {PIXEL_COLORS["text_soft"]};
                border-top: 1px solid {PIXEL_COLORS["border"]};
            }}
            """
        )