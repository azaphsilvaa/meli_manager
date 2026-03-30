from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from services.live_monitor_service import LiveMonitorService
from services.operation_log_service import OperationLogService


class DashboardPage(QWidget):
    toggle_monitor_requested = Signal()

    def __init__(self):
        super().__init__()

        self.monitor_service = LiveMonitorService()
        self.log_service = OperationLogService()

        self._setup_ui()
        self.refresh_monitor_status()
        self.refresh_logs()

    def _setup_ui(self):
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(16)
        self.setLayout(root_layout)

        header_card = QFrame()
        header_card.setObjectName("pageCard")

        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(18, 18, 18, 18)
        header_layout.setSpacing(6)
        header_card.setLayout(header_layout)

        title = QLabel("Dashboard")
        title.setObjectName("panelTitle")

        subtitle = QLabel("Visão geral do sistema e dos próximos módulos.")
        subtitle.setObjectName("cardDescription")
        subtitle.setWordWrap(True)

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)

        root_layout.addWidget(header_card)

        stats_grid = QGridLayout()
        stats_grid.setHorizontalSpacing(16)
        stats_grid.setVerticalSpacing(16)

        stats_grid.addWidget(
            self._create_stat_card(
                "Vendas Hoje",
                "0",
                "As vendas reais aparecerão aqui futuramente.",
            ),
            0,
            0,
        )

        stats_grid.addWidget(
            self._create_stat_card(
                "Pendentes",
                "0",
                "Pedidos aguardando processamento.",
            ),
            0,
            1,
        )

        stats_grid.addWidget(
            self._create_stat_card(
                "Etiquetas",
                "0",
                "Etiquetas prontas para baixar/imprimir.",
            ),
            1,
            0,
        )

        stats_grid.addWidget(
            self._create_stat_card(
                "Erros",
                "0",
                "Falhas de automação e integrações.",
            ),
            1,
            1,
        )

        root_layout.addLayout(stats_grid)

        monitor_card = QFrame()
        monitor_card.setObjectName("pageCard")

        monitor_layout = QVBoxLayout()
        monitor_layout.setContentsMargins(18, 18, 18, 18)
        monitor_layout.setSpacing(10)
        monitor_card.setLayout(monitor_layout)

        monitor_title = QLabel("Monitoramento ao vivo")
        monitor_title.setObjectName("panelTitle")

        self.monitor_status_label = QLabel("Status: OFF")
        self.monitor_status_label.setObjectName("cardDescription")

        self.monitor_description_label = QLabel(
            "Monitoramento desligado. O sistema não deve processar automação ao vivo."
        )
        self.monitor_description_label.setObjectName("cardDescription")
        self.monitor_description_label.setWordWrap(True)

        self.toggle_monitor_button = QPushButton("Ligar monitoramento")
        self.toggle_monitor_button.setObjectName("primaryButton")
        self.toggle_monitor_button.clicked.connect(self._on_toggle_monitor_clicked)

        monitor_layout.addWidget(monitor_title)
        monitor_layout.addWidget(self.monitor_status_label)
        monitor_layout.addWidget(self.monitor_description_label)
        monitor_layout.addSpacing(4)
        monitor_layout.addWidget(self.toggle_monitor_button)

        root_layout.addWidget(monitor_card)

        logs_card = QFrame()
        logs_card.setObjectName("pageCard")

        logs_layout = QVBoxLayout()
        logs_layout.setContentsMargins(18, 18, 18, 18)
        logs_layout.setSpacing(10)
        logs_card.setLayout(logs_layout)

        logs_title = QLabel("Logs operacionais")
        logs_title.setObjectName("panelTitle")

        self.last_notification_label = QLabel("Última notificação: -")
        self.last_notification_label.setObjectName("cardDescription")
        self.last_notification_label.setWordWrap(True)

        self.last_order_label = QLabel("Último pedido: -")
        self.last_order_label.setObjectName("cardDescription")
        self.last_order_label.setWordWrap(True)

        self.last_shipment_label = QLabel("Último shipment: -")
        self.last_shipment_label.setObjectName("cardDescription")
        self.last_shipment_label.setWordWrap(True)

        self.last_label_label = QLabel("Última etiqueta: -")
        self.last_label_label.setObjectName("cardDescription")
        self.last_label_label.setWordWrap(True)

        self.last_print_label = QLabel("Última impressão: -")
        self.last_print_label.setObjectName("cardDescription")
        self.last_print_label.setWordWrap(True)

        self.last_error_label = QLabel("Último erro: -")
        self.last_error_label.setObjectName("cardDescription")
        self.last_error_label.setWordWrap(True)

        logs_layout.addWidget(logs_title)
        logs_layout.addWidget(self.last_notification_label)
        logs_layout.addWidget(self.last_order_label)
        logs_layout.addWidget(self.last_shipment_label)
        logs_layout.addWidget(self.last_label_label)
        logs_layout.addWidget(self.last_print_label)
        logs_layout.addWidget(self.last_error_label)

        root_layout.addWidget(logs_card)
        root_layout.addStretch()

    def _create_stat_card(self, title: str, value: str, description: str):
        card = QFrame()
        card.setObjectName("pageCard")
        card.setMinimumHeight(150)

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(8)
        card.setLayout(layout)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")

        value_label = QLabel(value)
        value_label.setObjectName("cardValue")

        description_label = QLabel(description)
        description_label.setObjectName("cardDescription")
        description_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()
        layout.addWidget(description_label)

        return card

    def _on_toggle_monitor_clicked(self):
        self.toggle_monitor_requested.emit()

    def refresh_monitor_status(self):
        is_enabled = self.monitor_service.get_status()

        if is_enabled:
            self.monitor_status_label.setText("Status: ON")
            self.monitor_description_label.setText(
                "Monitoramento ativo. O sistema está autorizado a operar automações ao vivo."
            )
            self.toggle_monitor_button.setText("Desligar monitoramento")
        else:
            self.monitor_status_label.setText("Status: OFF")
            self.monitor_description_label.setText(
                "Monitoramento desligado. O sistema não deve processar automação ao vivo."
            )
            self.toggle_monitor_button.setText("Ligar monitoramento")

    def refresh_logs(self):
        logs = self.log_service.get_logs()

        self.last_notification_label.setText(
            self._format_log_text("Última notificação", logs.get("last_notification"))
        )

        self.last_order_label.setText(
            self._format_log_text("Último pedido", logs.get("last_order"))
        )

        self.last_shipment_label.setText(
            self._format_log_text("Último shipment", logs.get("last_shipment"))
        )

        self.last_label_label.setText(
            self._format_log_text("Última etiqueta", logs.get("last_label"))
        )

        self.last_print_label.setText(
            self._format_log_text("Última impressão", logs.get("last_print"))
        )

        self.last_error_label.setText(
            self._format_log_text("Último erro", logs.get("last_error"))
        )

    def _format_log_text(self, title: str, item: dict | None) -> str:
        if not item:
            return f"{title}: -"

        text = item.get("text") or "-"
        timestamp = item.get("timestamp") or "-"

        return f"{title}: {text} | {timestamp}"