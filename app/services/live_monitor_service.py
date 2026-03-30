import json
import os


class LiveMonitorService:
    SETTINGS_FILE = os.path.join("data", "live_monitor_settings.json")

    def get_status(self) -> bool:
        if not os.path.exists(self.SETTINGS_FILE):
            return False

        try:
            with open(self.SETTINGS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                return bool(data.get("is_enabled", False))
        except Exception:
            return False

    def set_status(self, is_enabled: bool) -> bool:
        try:
            os.makedirs("data", exist_ok=True)

            with open(self.SETTINGS_FILE, "w", encoding="utf-8") as file:
                json.dump(
                    {"is_enabled": bool(is_enabled)},
                    file,
                    ensure_ascii=False,
                    indent=4,
                )

            return True

        except Exception as error:
            print(f"Erro ao salvar status do monitoramento: {error}")
            return False

    def toggle_status(self) -> bool:
        current_status = self.get_status()
        new_status = not current_status

        saved = self.set_status(new_status)

        if not saved:
            return current_status

        return new_status