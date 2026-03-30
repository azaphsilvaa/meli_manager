import webbrowser

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config.app_info import APP_NAME, APP_VERSION
from services.github_update_service import GitHubUpdateService


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.update_service = GitHubUpdateService()

        self._setup_ui()

    def _setup_ui(self):
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(16)
        self.setLayout(root_layout)

        header_card = QFrame()
        header_card.setObjectName("pageCard")

        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(18, 18, 18, 18)
        header_layout.setSpacing(8)
        header_card.setLayout(header_layout)

        title = QLabel("Configurações")
        title.setObjectName("panelTitle")

        subtitle = QLabel("Versão do app, atualizações e manutenção.")
        subtitle.setObjectName("cardDescription")

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)

        root_layout.addWidget(header_card)

        update_card = QFrame()
        update_card.setObjectName("pageCard")

        update_layout = QVBoxLayout()
        update_layout.setContentsMargins(18, 18, 18, 18)
        update_layout.setSpacing(10)
        update_card.setLayout(update_layout)

        update_title = QLabel("Atualizações")
        update_title.setObjectName("panelTitle")

        self.current_version_label = QLabel(f"Versão atual: {APP_VERSION}")
        self.current_version_label.setObjectName("cardDescription")

        self.latest_version_label = QLabel("Última versão encontrada: -")
        self.latest_version_label.setObjectName("cardDescription")

        self.update_status_label = QLabel("Status: ainda não verificado")
        self.update_status_label.setObjectName("cardDescription")
        self.update_status_label.setWordWrap(True)

        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(10)

        self.check_updates_button = QPushButton("Verificar atualização")
        self.check_updates_button.setObjectName("primaryButton")
        self.check_updates_button.clicked.connect(self._check_updates)

        self.download_update_button = QPushButton("Baixar atualização")
        self.download_update_button.setObjectName("primaryButton")
        self.download_update_button.setEnabled(False)
        self.download_update_button.clicked.connect(self._download_update)

        buttons_row.addWidget(self.check_updates_button)
        buttons_row.addWidget(self.download_update_button)
        buttons_row.addStretch()

        update_layout.addWidget(update_title)
        update_layout.addWidget(self.current_version_label)
        update_layout.addWidget(self.latest_version_label)
        update_layout.addWidget(self.update_status_label)
        update_layout.addLayout(buttons_row)

        root_layout.addWidget(update_card)
        root_layout.addStretch()

        self.latest_download_url = None

    def _check_updates(self):
        result = self.update_service.check_for_updates()

        if not result["success"]:
            self.latest_version_label.setText("Última versão encontrada: -")
            self.update_status_label.setText(f"Status: {result['message']}")
            self.download_update_button.setEnabled(False)
            self.latest_download_url = None
            return

        self.latest_version_label.setText(
            f"Última versão encontrada: {result['latest_version']}"
        )

        if result["update_available"]:
            self.update_status_label.setText(
                "Status: atualização disponível no GitHub."
            )
            self.latest_download_url = result["download_url"]
            self.download_update_button.setEnabled(True)
        else:
            self.update_status_label.setText(
                "Status: você já está na versão mais recente."
            )
            self.latest_download_url = None
            self.download_update_button.setEnabled(False)

    def _download_update(self):
        if not self.latest_download_url:
            QMessageBox.information(
                self,
                APP_NAME,
                "Nenhum link de atualização disponível no momento.",
            )
            return

        webbrowser.open(self.latest_download_url)