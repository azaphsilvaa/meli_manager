from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from services.order_service import OrderService


class SalesPage(QWidget):
    create_test_order_requested = Signal()
    remove_order_requested = Signal(str)
    reprocess_order_requested = Signal(str, str)

    def __init__(self):
        super().__init__()

        self.order_service = OrderService()

        self._setup_ui()
        self.load_orders()

    def _setup_ui(self):
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(16)
        self.setLayout(root_layout)

        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        self.title_label = QLabel("Vendas")
        self.title_label.setObjectName("panelTitle")

        self.create_test_button = QPushButton("Criar venda teste")
        self.create_test_button.setObjectName("primaryButton")
        self.create_test_button.clicked.connect(self._on_create_test_order_clicked)

        self.refresh_button = QPushButton("Atualizar lista")
        self.refresh_button.setObjectName("primaryButton")
        self.refresh_button.clicked.connect(self.load_orders)

        top_bar.addWidget(self.title_label)
        top_bar.addStretch()
        top_bar.addWidget(self.create_test_button)
        top_bar.addWidget(self.refresh_button)

        self.info_label = QLabel("Nenhuma venda carregada ainda.")
        self.info_label.setObjectName("cardDescription")

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("salesScrollArea")

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(14)
        self.scroll_content.setLayout(self.scroll_layout)

        self.scroll_area.setWidget(self.scroll_content)

        root_layout.addLayout(top_bar)
        root_layout.addWidget(self.info_label)
        root_layout.addWidget(self.scroll_area)

    def _on_create_test_order_clicked(self):
        self.create_test_order_requested.emit()

    def clear_orders_list(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def load_orders(self):
        self.clear_orders_list()

        orders = self.order_service.list_orders()

        if not orders:
            self.info_label.setText("Nenhuma venda cadastrada no momento.")
            empty_card = self._create_empty_card()
            self.scroll_layout.addWidget(empty_card)
            self.scroll_layout.addStretch()
            return

        self.info_label.setText(f"{len(orders)} venda(s) cadastrada(s).")

        for order in orders:
            card = self._create_order_card(order)
            self.scroll_layout.addWidget(card)

        self.scroll_layout.addStretch()

    def _create_empty_card(self):
        card = QFrame()
        card.setObjectName("pageCard")

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(8)
        card.setLayout(layout)

        title = QLabel("Nenhuma venda encontrada")
        title.setObjectName("cardTitle")

        description = QLabel(
            "Quando sincronizarmos as vendas do Mercado Livre, elas aparecerão aqui."
        )
        description.setObjectName("cardDescription")
        description.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(description)

        return card

    def _create_order_card(self, order):
        card = QFrame()
        card.setObjectName("pageCard")

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
        card.setLayout(layout)

        header_row = QHBoxLayout()
        header_row.setSpacing(10)

        title = QLabel(order.item_title or "Venda sem título")
        title.setObjectName("cardTitle")

        status_text = order.order_status or "SEM STATUS"
        status_label = QLabel(status_text.upper())
        status_label.setObjectName("accountStatusLabel")

        header_row.addWidget(title)
        header_row.addStretch()
        header_row.addWidget(status_label)

        order_id = QLabel(f"Order ID: {order.ml_order_id}")
        order_id.setObjectName("cardDescription")

        account_info = QLabel(
            f"Conta: {order.account_nickname or order.account_user_id or '-'}"
        )
        account_info.setObjectName("cardDescription")

        buyer_info = QLabel(
            f"Comprador: {order.buyer_name or order.buyer_nickname or '-'}"
        )
        buyer_info.setObjectName("cardDescription")

        quantity_info = QLabel(f"Quantidade: {order.item_quantity or 0}")
        quantity_info.setObjectName("cardDescription")

        amount_info = QLabel(
            f"Valor total: R$ {order.total_amount:.2f}"
            if order.total_amount is not None
            else "Valor total: -"
        )
        amount_info.setObjectName("cardDescription")

        shipping_info = QLabel(f"Envio: {order.shipping_status or '-'}")
        shipping_info.setObjectName("cardDescription")

        payment_info = QLabel(f"Pagamento: {order.payment_status or '-'}")
        payment_info.setObjectName("cardDescription")

        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)

        reprocess_button = QPushButton("Reprocessar")
        reprocess_button.setObjectName("primaryButton")
        reprocess_button.clicked.connect(
            lambda _, ml_order_id=order.ml_order_id, user_id=order.account_user_id: (
                self._on_reprocess_order_clicked(ml_order_id, user_id)
            )
        )

        remove_button = QPushButton("Remover")
        remove_button.setObjectName("primaryButton")
        remove_button.clicked.connect(
            lambda _, ml_order_id=order.ml_order_id: (
                self._on_remove_order_clicked(ml_order_id)
            )
        )

        actions_row.addWidget(reprocess_button)
        actions_row.addWidget(remove_button)
        actions_row.addStretch()

        layout.addLayout(header_row)
        layout.addWidget(order_id)
        layout.addWidget(account_info)
        layout.addWidget(buyer_info)
        layout.addWidget(quantity_info)
        layout.addWidget(amount_info)
        layout.addWidget(shipping_info)
        layout.addWidget(payment_info)
        layout.addSpacing(4)
        layout.addLayout(actions_row)

        return card

    def _on_remove_order_clicked(self, ml_order_id: str):
        reply = QMessageBox.question(
            self,
            "Remover venda",
            f"Deseja remover a venda '{ml_order_id}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.remove_order_requested.emit(ml_order_id)

    def _on_reprocess_order_clicked(self, ml_order_id: str, user_id: str | None):
        if not user_id:
            QMessageBox.warning(
                self,
                "Conta ausente",
                "Essa venda não possui account_user_id para reprocessar.",
            )
            return

        reply = QMessageBox.question(
            self,
            "Reprocessar venda",
            (
                f"Deseja reprocessar a venda '{ml_order_id}'?\n\n"
                "Isso vai buscar pedido real, shipment real e tentar baixar/imprimir etiqueta."
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )

        if reply == QMessageBox.Yes:
            self.reprocess_order_requested.emit(ml_order_id, user_id)