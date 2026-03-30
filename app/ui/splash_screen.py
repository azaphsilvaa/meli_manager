import os

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt, QTimer
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from ui.theme import PIXEL_COLORS


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.progress_value = 0
        self._setup_ui()
        self._apply_styles()
        self._start_loading()

    def _setup_ui(self):
        self.setWindowTitle("Meli Manager - Carregando")
        self.setFixedSize(1200, 700)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.setLayout(root_layout)

        self.background_label = QLabel()
        self.background_label.setObjectName("backgroundLabel")
        self.background_label.setAlignment(Qt.AlignCenter)
        self.background_label.setScaledContents(True)

        gif_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "assets",
                "images",
                "loading_bg.gif",
            )
        )

        self.movie = QMovie(gif_path)
        self.movie.setScaledSize(QSize(1200, 700))
        self.background_label.setMovie(self.movie)
        self.movie.start()

        overlay = QFrame(self.background_label)
        overlay.setObjectName("overlay")
        overlay.setGeometry(0, 0, 1200, 700)

        overlay_layout = QHBoxLayout()
        overlay_layout.setContentsMargins(60, 60, 60, 60)
        overlay.setLayout(overlay_layout)

        overlay_layout.addStretch()

        panel_wrapper = QVBoxLayout()
        panel_wrapper.addStretch()

        self.loading_panel = QFrame()
        self.loading_panel.setObjectName("loadingPanel")
        self.loading_panel.setFixedSize(360, 180)

        panel_layout = QVBoxLayout()
        panel_layout.setContentsMargins(24, 24, 24, 24)
        panel_layout.setSpacing(14)
        self.loading_panel.setLayout(panel_layout)

        title = QLabel("SOFTWARE ML")
        title.setObjectName("loadingTitle")

        subtitle = QLabel("Inicializando SOFTWARE ML...")
        subtitle.setObjectName("loadingSubtitle")

        self.status_label = QLabel("Carregando interface...")
        self.status_label.setObjectName("loadingStatus")

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(18)
        self.progress.setObjectName("loadingProgress")

        panel_layout.addWidget(title)
        panel_layout.addWidget(subtitle)
        panel_layout.addSpacing(4)
        panel_layout.addWidget(self.status_label)
        panel_layout.addWidget(self.progress)

        panel_wrapper.addWidget(self.loading_panel, alignment=Qt.AlignRight | Qt.AlignVCenter)
        panel_wrapper.addStretch()

        overlay_layout.addLayout(panel_wrapper)

        root_layout.addWidget(self.background_label)

        self.overlay = overlay

        self.opacity_effect = QGraphicsOpacityEffect()
        self.loading_panel.setGraphicsEffect(self.opacity_effect)

        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(900)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.start()

        self._update_background_scaling()

    def _update_background_scaling(self):
        current_size = self.size()

        self.background_label.setFixedSize(current_size)
        self.movie.setScaledSize(current_size)

        if hasattr(self, "overlay"):
            self.overlay.setGeometry(0, 0, current_size.width(), current_size.height())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_background_scaling()

    def showEvent(self, event):
        super().showEvent(event)
        self._update_background_scaling()

    def _start_loading(self):
        self.loading_steps = [
            (15, "Carregando interface..."),
            (35, "Aplicando tema pixel art..."),
            (55, "Preparando componentes..."),
            (75, "Organizando painel principal..."),
            (90, "Finalizando abertura..."),
            (100, "Tudo pronto."),
        ]

        self.step_index = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_loading)
        self.timer.start(350)

    def _update_loading(self):
        if self.step_index < len(self.loading_steps):
            value, text = self.loading_steps[self.step_index]
            self.progress.setValue(value)
            self.status_label.setText(text)
            self.step_index += 1
        else:
            self.timer.stop()

    def _apply_styles(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {PIXEL_COLORS["bg_main"]};
            }}

            #backgroundLabel {{
                background-color: {PIXEL_COLORS["bg_main"]};
            }}

            #overlay {{
                background-color: rgba(4, 10, 20, 70);
            }}

            #loadingPanel {{
                background-color: rgba(10, 22, 40, 220);
                border: 2px solid {PIXEL_COLORS["border"]};
                border-radius: 14px;
            }}

            #loadingTitle {{
                color: {PIXEL_COLORS["text_main"]};
                font-size: 26px;
                font-weight: 700;
            }}

            #loadingSubtitle {{
                color: {PIXEL_COLORS["primary"]};
                font-size: 14px;
                font-weight: 600;
            }}

            #loadingStatus {{
                color: {PIXEL_COLORS["text_soft"]};
                font-size: 13px;
            }}

            #loadingProgress {{
                background-color: {PIXEL_COLORS["bg_card"]};
                border: 1px solid {PIXEL_COLORS["border"]};
                border-radius: 8px;
            }}

            #loadingProgress::chunk {{
                background-color: {PIXEL_COLORS["primary"]};
                border-radius: 6px;
            }}
        """)