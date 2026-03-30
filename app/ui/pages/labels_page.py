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

from services.label_file_service import LabelFileService
from services.label_print_control_service import LabelPrintControlService


class LabelsPage(QWidget):
    reprint_label_requested = Signal(str)
    remove_label_requested = Signal(str)

    def __init__(self):
        super().__init__()

        self.label_service = LabelFileService()
        self.print_control_service = LabelPrintControlService()

        self._setup_ui()
        self.load_labels()

    def _setup_ui(self):
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(16)
        self.setLayout(root_layout)

        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        self.title_label = QLabel("Etiquetas")
        self.title_label.setObjectName("panelTitle")

        self.refresh_button = QPushButton("Atualizar lista")
        self.refresh_button.setObjectName("primaryButton")
        self.refresh_button.clicked.connect(self.load_labels)

        top_bar.addWidget(self.title_label)
        top_bar.addStretch()
        top_bar.addWidget(self.refresh_button)

        self.info_label = QLabel("Nenhuma etiqueta carregada ainda.")
        self.info_label.setObjectName("cardDescription")

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("labelsScrollArea")

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(14)
        self.scroll_content.setLayout(self.scroll_layout)

        self.scroll_area.setWidget(self.scroll_content)

        root_layout.addLayout(top_bar)
        root_layout.addWidget(self.info_label)
        root_layout.addWidget(self.scroll_area)

    def clear_labels_list(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def load_labels(self):
        self.clear_labels_list()

        labels = self.label_service.list_labels()

        if not labels:
            self.info_label.setText("Nenhuma etiqueta encontrada na pasta local.")
            empty_card = self._create_empty_card()
            self.scroll_layout.addWidget(empty_card)
            self.scroll_layout.addStretch()
            return

        self.info_label.setText(f"{len(labels)} etiqueta(s) encontrada(s).")

        for label_data in labels:
            card = self._create_label_card(label_data)
            self.scroll_layout.addWidget(card)

        self.scroll_layout.addStretch()

    def _create_empty_card(self):
        card = QFrame()
        card.setObjectName("pageCard")

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(8)
        card.setLayout(layout)

        title = QLabel("Nenhuma etiqueta encontrada")
        title.setObjectName("cardTitle")

        description = QLabel(
            "Quando o sistema baixar etiquetas em PDF, elas aparecerão aqui."
        )
        description.setObjectName("cardDescription")
        description.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(description)

        return card

    def _create_label_card(self, label_data: dict):
        card = QFrame()
        card.setObjectName("pageCard")

        print_status = self.print_control_service.get_label_status(label_data["file_path"])

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
        card.setLayout(layout)

        header_row = QHBoxLayout()
        header_row.setSpacing(10)

        title = QLabel(label_data["file_name"])
        title.setObjectName("cardTitle")

        if print_status["is_printed"]:
            status_text = "IMPRESSA"
        else:
            status_text = "NÃO IMPRESSA"

        status_label = QLabel(status_text)
        status_label.setObjectName("accountStatusLabel")

        header_row.addWidget(title)
        header_row.addStretch()
        header_row.addWidget(status_label)

        modified_at = label_data["modified_at"].strftime("%d/%m/%Y %H:%M:%S")
        modified_label = QLabel(f"Modificado em: {modified_at}")
        modified_label.setObjectName("cardDescription")

        size_kb = label_data["size_bytes"] / 1024
        size_label = QLabel(f"Tamanho: {size_kb:.1f} KB")
        size_label.setObjectName("cardDescription")

        printed_at = print_status["printed_at"] or "-"
        printed_label = QLabel(f"Última impressão: {printed_at}")
        printed_label.setObjectName("cardDescription")

        path_label = QLabel(f"Caminho: {label_data['file_path']}")
        path_label.setObjectName("cardDescription")
        path_label.setWordWrap(True)

        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)

        reprint_button = QPushButton("Reimprimir")
        reprint_button.setObjectName("primaryButton")
        reprint_button.clicked.connect(
            lambda _, file_path=label_data["file_path"]: self._on_reprint_clicked(file_path)
        )

        remove_button = QPushButton("Remover")
        remove_button.setObjectName("primaryButton")
        remove_button.clicked.connect(
            lambda _, file_path=label_data["file_path"]: self._on_remove_clicked(file_path)
        )

        actions_row.addWidget(reprint_button)
        actions_row.addWidget(remove_button)
        actions_row.addStretch()

        layout.addLayout(header_row)
        layout.addWidget(modified_label)
        layout.addWidget(size_label)
        layout.addWidget(printed_label)
        layout.addWidget(path_label)
        layout.addSpacing(4)
        layout.addLayout(actions_row)

        return card

    def _on_reprint_clicked(self, file_path: str):
        self.reprint_label_requested.emit(file_path)

    def _on_remove_clicked(self, file_path: str):
        reply = QMessageBox.question(
            self,
            "Remover etiqueta",
            f"Deseja remover este PDF?\n\n{file_path}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.remove_label_requested.emit(file_path)