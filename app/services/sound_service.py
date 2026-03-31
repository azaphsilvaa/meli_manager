import os

from PySide6.QtCore import QEvent, QObject, QUrl
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import QListWidget, QPushButton, QWidget


class SoundService:
    def __init__(self):
        self.click_sound = QSoundEffect()
        self.loading_sound = QSoundEffect()
        self.success_sound = QSoundEffect()
        self.error_sound = QSoundEffect()
        self.notification_sound = QSoundEffect()

        self._configure_sound(
            sound=self.click_sound,
            file_path=os.path.join("assets", "sounds", "click.wav"),
            volume=0.30,
            loop_count=1,
        )

        self._configure_sound(
            sound=self.loading_sound,
            file_path=os.path.join("assets", "sounds", "loading.wav"),
            volume=0.12,
            loop_count=-2,
        )

        self._configure_sound(
            sound=self.success_sound,
            file_path=os.path.join("assets", "sounds", "success.wav"),
            volume=0.24,
            loop_count=1,
        )

        self._configure_sound(
            sound=self.error_sound,
            file_path=os.path.join("assets", "sounds", "error.wav"),
            volume=0.22,
            loop_count=1,
        )

        self._configure_sound(
            sound=self.notification_sound,
            file_path=os.path.join("assets", "sounds", "notification.wav"),
            volume=0.20,
            loop_count=1,
        )

    def _configure_sound(
        self,
        sound: QSoundEffect,
        file_path: str,
        volume: float,
        loop_count: int,
    ):
        if os.path.exists(file_path):
            sound.setSource(QUrl.fromLocalFile(os.path.abspath(file_path)))

        sound.setVolume(volume)
        sound.setLoopCount(loop_count)

    def play_click(self):
        if self.click_sound.source().isEmpty():
            return

        self.click_sound.stop()
        self.click_sound.play()

    def play_success(self):
        if self.success_sound.source().isEmpty():
            return

        self.success_sound.stop()
        self.success_sound.play()

    def play_error(self):
        if self.error_sound.source().isEmpty():
            return

        self.error_sound.stop()
        self.error_sound.play()

    def play_notification(self):
        if self.notification_sound.source().isEmpty():
            return

        self.notification_sound.stop()
        self.notification_sound.play()

    def start_loading_loop(self):
        if self.loading_sound.source().isEmpty():
            return

        self.loading_sound.stop()
        self.loading_sound.play()

    def stop_loading_loop(self):
        self.loading_sound.stop()


class UiSoundEventFilter(QObject):
    def __init__(self, sound_service: SoundService):
        super().__init__()
        self.sound_service = sound_service

    def eventFilter(self, watched, event):
        if event.type() == QEvent.MouseButtonPress:

            if isinstance(watched, QPushButton):
                self.sound_service.play_click()
                return super().eventFilter(watched, event)

            if isinstance(watched, QListWidget):
                self.sound_service.play_click()
                return super().eventFilter(watched, event)

            parent_widget = watched.parent()

            if isinstance(parent_widget, QListWidget):
                self.sound_service.play_click()
                return super().eventFilter(watched, event)

            grandparent_widget = parent_widget.parent() if parent_widget else None

            if isinstance(grandparent_widget, QListWidget):
                self.sound_service.play_click()
                return super().eventFilter(watched, event)

        return super().eventFilter(watched, event)