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

from services.printer_service import PrinterService


class PrintersPage(QWidget):
    select_printer_requested = Signal(str)

    def __init__(self):
        super().__init__()

        self.printer_service = PrinterService()

        self._setup_ui()
        self.load_printers()

    def _setup_ui(self):
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(16)
        self.setLayout(root_layout)

        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        self.title_label = QLabel("Impressoras")
        self.title_label.setObjectName("panelTitle")

        self.refresh_button = QPushButton("Atualizar lista")
        self.refresh_button.setObjectName("primaryButton")
        self.refresh_button.clicked.connect(self.load_printers)

        top_bar.addWidget(self.title_label)
        top_bar.addStretch()
        top_bar.addWidget(self.refresh_button)

        self.info_label = QLabel("Nenhuma impressora carregada ainda.")
        self.info_label.setObjectName("cardDescription")

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("printersScrollArea")

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(14)
        self.scroll_content.setLayout(self.scroll_layout)

        self.scroll_area.setWidget(self.scroll_content)

        root_layout.addLayout(top_bar)
        root_layout.addWidget(self.info_label)
        root_layout.addWidget(self.scroll_area)
        
    def _on_test_print_clicked(self, printer_name: str):

        try:
            self.printer_service.print_test_page(printer_name)

            QMessageBox.information(
                self,
                "Teste enviado",
                f"Teste enviado para impressora:\n{printer_name}",
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao imprimir teste:\n{error}",
            )

    def clear_printers_list(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def load_printers(self):
        self.clear_printers_list()

        printers = self.printer_service.list_printers()

        if not printers:
            self.info_label.setText("Nenhuma impressora encontrada no Windows.")
            empty_card = self._create_empty_card()
            self.scroll_layout.addWidget(empty_card)
            self.scroll_layout.addStretch()
            return

        self.info_label.setText(f"{len(printers)} impressora(s) encontrada(s).")

        for printer in printers:
            card = self._create_printer_card(printer)
            self.scroll_layout.addWidget(card)

        self.scroll_layout.addStretch()

    def _create_empty_card(self):
        card = QFrame()
        card.setObjectName("pageCard")

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(8)
        card.setLayout(layout)

        title = QLabel("Nenhuma impressora encontrada")
        title.setObjectName("cardTitle")

        description = QLabel(
            "Conecte ou instale uma impressora no Windows para ela aparecer aqui."
        )
        description.setObjectName("cardDescription")
        description.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(description)

        return card

    def _create_printer_card(self, printer: dict):
        card = QFrame()
        card.setObjectName("pageCard")

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
        card.setLayout(layout)

        header_row = QHBoxLayout()
        header_row.setSpacing(10)

        title = QLabel(printer["name"])
        title.setObjectName("cardTitle")

        status_parts = []

        if printer["is_windows_default"]:
            status_parts.append("PADRÃO WINDOWS")

        if printer["is_selected"]:
            status_parts.append("SELECIONADA NO APP")

        status_text = " • ".join(status_parts) if status_parts else "DISPONÍVEL"

        status_label = QLabel(status_text)
        status_label.setObjectName("accountStatusLabel")

        header_row.addWidget(title)
        header_row.addStretch()
        header_row.addWidget(status_label)

        details = QLabel(
            "Use esta impressora para etiquetas automáticas do SOFTWARE ML."
        )
        details.setObjectName("cardDescription")
        details.setWordWrap(True)

        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)

        select_button = QPushButton("Selecionar")
        select_button.setObjectName("primaryButton")
        select_button.clicked.connect(
            lambda _, name=printer["name"]: self._on_select_printer_clicked(name)
        )

        test_button = QPushButton("Imprimir teste")
        test_button.setObjectName("secondaryButton")
        test_button.clicked.connect(
            lambda _, name=printer["name"]: self._on_test_print_clicked(name)
        )

        actions_row.addWidget(select_button)
        actions_row.addWidget(test_button)
        actions_row.addStretch()

        layout.addLayout(header_row)
        layout.addWidget(details)
        layout.addSpacing(4)
        layout.addLayout(actions_row)

        return card

    def _on_select_printer_clicked(self, printer_name: str):
        reply = QMessageBox.question(
            self,
            "Selecionar impressora",
            f"Deseja definir '{printer_name}' como impressora do SOFTWARE ML?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )

        if reply == QMessageBox.Yes:
            self.select_printer_requested.emit(printer_name)