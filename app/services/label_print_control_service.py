import json
import os
from datetime import datetime


class LabelPrintControlService:
    SETTINGS_FILE = os.path.join("data", "label_print_control.json")

    def _load_data(self) -> dict:
        if not os.path.exists(self.SETTINGS_FILE):
            return {}

        try:
            with open(self.SETTINGS_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return {}

    def _save_data(self, data: dict) -> bool:
        try:
            os.makedirs("data", exist_ok=True)

            with open(self.SETTINGS_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            return True
        except Exception as error:
            print(f"Erro ao salvar controle de impressão: {error}")
            return False

    def mark_as_printed(self, file_path: str) -> bool:
        data = self._load_data()

        data[file_path] = {
            "is_printed": True,
            "printed_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        }

        return self._save_data(data)

    def get_label_status(self, file_path: str) -> dict:
        data = self._load_data()

        if file_path not in data:
            return {
                "is_printed": False,
                "printed_at": None,
            }

        item = data[file_path]

        return {
            "is_printed": bool(item.get("is_printed", False)),
            "printed_at": item.get("printed_at"),
        }

    def remove_label_record(self, file_path: str) -> bool:
        data = self._load_data()

        if file_path in data:
            del data[file_path]

        return self._save_data(data)