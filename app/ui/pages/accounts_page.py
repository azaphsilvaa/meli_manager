from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from services.account_service import AccountService


class EditAccountDialog(QDialog):
    def __init__(self, current_name: str = "", current_description: str = "", parent=None):
        super().__init__(parent)

        self.setWindowTitle("Editar conta")
        self.setMinimumWidth(460)

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        self.setLayout(layout)

        title = QLabel("Editar informações personalizadas da conta")
        title.setObjectName("cardTitle")

        subtitle = QLabel(
            "Você pode editar apenas o nome, apenas a descrição, os dois, ou deixar vazio para limpar."
        )
        subtitle.setObjectName("cardDescription")
        subtitle.setWordWrap(True)

        name_label = QLabel("Nome personalizado")
        name_label.setObjectName("cardDescription")

        self.name_input = QLineEdit()
        self.name_input.setText(current_name or "")
        self.name_input.setPlaceholderText("Ex: Loja Principal")
        self.name_input.setMinimumHeight(38)

        description_label = QLabel("Descrição")
        description_label.setObjectName("cardDescription")

        self.description_input = QTextEdit()
        self.description_input.setPlainText(current_description or "")
        self.description_input.setPlaceholderText("Ex: Conta usada para vendas principais")
        self.description_input.setMinimumHeight(120)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(4)
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(description_label)
        layout.addWidget(self.description_input)
        layout.addSpacing(6)
        layout.addWidget(buttons)

    def get_values(self):
        return (
            self.name_input.text().strip(),
            self.description_input.toPlainText().strip(),
        )


class AccountsPage(QWidget):
    connect_account_requested = Signal()
    refresh_all_tokens_requested = Signal()
    refresh_token_requested = Signal(int)
    remove_account_requested = Signal(int)
    edit_account_requested = Signal(int, str, str)

    def __init__(self):
        super().__init__()

        self.account_service = AccountService()

        self._setup_ui()
        self.load_accounts()

    def _setup_ui(self):
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(16)
        self.setLayout(root_layout)

        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        self.title_label = QLabel("Contas conectadas")
        self.title_label.setObjectName("panelTitle")

        self.connect_button = QPushButton("Conectar conta")
        self.connect_button.setObjectName("primaryButton")
        self.connect_button.clicked.connect(self._on_connect_account_clicked)

        self.refresh_all_button = QPushButton("Refresh todas")
        self.refresh_all_button.setObjectName("primaryButton")
        self.refresh_all_button.clicked.connect(self._on_refresh_all_clicked)

        self.refresh_button = QPushButton("Atualizar lista")
        self.refresh_button.setObjectName("primaryButton")
        self.refresh_button.clicked.connect(self.load_accounts)

        top_bar.addWidget(self.title_label)
        top_bar.addStretch()
        top_bar.addWidget(self.connect_button)
        top_bar.addWidget(self.refresh_all_button)
        top_bar.addWidget(self.refresh_button)

        self.info_label = QLabel("Nenhuma conta carregada ainda.")
        self.info_label.setObjectName("cardDescription")

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("accountsScrollArea")

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(14)
        self.scroll_content.setLayout(self.scroll_layout)

        self.scroll_area.setWidget(self.scroll_content)

        root_layout.addLayout(top_bar)
        root_layout.addWidget(self.info_label)
        root_layout.addWidget(self.scroll_area)

    def _on_connect_account_clicked(self):
        self.connect_account_requested.emit()

    def _on_refresh_all_clicked(self):
        self.refresh_all_tokens_requested.emit()

    def clear_accounts_list(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def load_accounts(self):
        self.clear_accounts_list()

        accounts = self.account_service.list_accounts()

        if not accounts:
            self.info_label.setText("Nenhuma conta cadastrada no momento.")
            empty_card = self._create_empty_card()
            self.scroll_layout.addWidget(empty_card)
            self.scroll_layout.addStretch()
            return

        self.info_label.setText(f"{len(accounts)} conta(s) cadastrada(s).")

        for account in accounts:
            card = self._create_account_card(account)
            self.scroll_layout.addWidget(card)

        self.scroll_layout.addStretch()

    def _create_empty_card(self):
        card = QFrame()
        card.setObjectName("pageCard")

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(8)
        card.setLayout(layout)

        title = QLabel("Nenhuma conta encontrada")
        title.setObjectName("cardTitle")

        description = QLabel(
            "Quando conectarmos contas do Mercado Livre, elas aparecerão aqui."
        )
        description.setObjectName("cardDescription")
        description.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(description)

        return card

    def _create_account_card(self, account):
        card = QFrame()
        card.setObjectName("pageCard")

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
        card.setLayout(layout)

        header_row = QHBoxLayout()
        header_row.setSpacing(10)

        display_name = account.custom_name or account.nickname or "Sem nickname"
        title = QLabel(display_name)
        title.setObjectName("cardTitle")

        status_text = "ATIVA" if account.is_active else "INATIVA"
        if account.is_default:
            status_text += " • PADRÃO"

        status_label = QLabel(status_text)
        status_label.setObjectName("accountStatusLabel")

        header_row.addWidget(title)
        header_row.addStretch()
        header_row.addWidget(status_label)

        user_id = QLabel(f"User ID: {account.user_id or '-'}")
        user_id.setObjectName("cardDescription")

        nickname = QLabel(f"Nickname ML: {account.nickname or '-'}")
        nickname.setObjectName("cardDescription")

        account_label = QLabel(f"Rótulo: {account.account_label or '-'}")
        account_label.setObjectName("cardDescription")

        seller_email = QLabel(f"E-mail: {account.seller_email or '-'}")
        seller_email.setObjectName("cardDescription")

        token_type = QLabel(f"Token Type: {account.token_type or '-'}")
        token_type.setObjectName("cardDescription")

        description_value = account.description or "-"
        description = QLabel(f"Descrição: {description_value}")
        description.setObjectName("cardDescription")
        description.setWordWrap(True)

        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)

        edit_button = QPushButton("Editar")
        edit_button.setObjectName("primaryButton")
        edit_button.clicked.connect(
            lambda _, acc=account: self._on_edit_account_clicked(acc)
        )

        refresh_token_button = QPushButton("Refresh token")
        refresh_token_button.setObjectName("primaryButton")
        refresh_token_button.clicked.connect(
            lambda _, account_id=account.id: self.refresh_token_requested.emit(account_id)
        )

        remove_button = QPushButton("Remover")
        remove_button.setObjectName("primaryButton")
        remove_button.clicked.connect(
            lambda _, acc=account: self._on_remove_account_clicked(acc)
        )

        actions_row.addWidget(edit_button)
        actions_row.addWidget(refresh_token_button)
        actions_row.addWidget(remove_button)
        actions_row.addStretch()

        layout.addLayout(header_row)
        layout.addWidget(user_id)
        layout.addWidget(nickname)
        layout.addWidget(account_label)
        layout.addWidget(seller_email)
        layout.addWidget(token_type)
        layout.addWidget(description)
        layout.addSpacing(4)
        layout.addLayout(actions_row)

        return card

    def _on_edit_account_clicked(self, account):
        dialog = EditAccountDialog(
            current_name=account.custom_name or "",
            current_description=account.description or "",
            parent=self,
        )

        if dialog.exec():
            custom_name, description = dialog.get_values()
            self.edit_account_requested.emit(account.id, custom_name, description)

    def _on_remove_account_clicked(self, account):
        display_name = account.custom_name or account.nickname or f"Conta {account.id}"

        reply = QMessageBox.question(
            self,
            "Remover conta",
            f"Deseja remover a conta '{display_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.remove_account_requested.emit(account.id)