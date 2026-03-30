import json
import os
from datetime import datetime


class OperationLogService:
    LOG_FILE = os.path.join("data", "operation_logs.json")

    def _default_data(self) -> dict:
        return {
            "last_notification": None,
            "last_order": None,
            "last_shipment": None,
            "last_label": None,
            "last_print": None,
            "last_error": None,
            "updated_at": None,
        }

    def _load_data(self) -> dict:
        if not os.path.exists(self.LOG_FILE):
            return self._default_data()

        try:
            with open(self.LOG_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            default_data = self._default_data()
            default_data.update(data)

            return default_data

        except Exception:
            return self._default_data()

    def _save_data(self, data: dict) -> bool:
        try:
            os.makedirs("data", exist_ok=True)

            data["updated_at"] = self._now()

            with open(self.LOG_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            return True

        except Exception as error:
            print(f"Erro ao salvar logs operacionais: {error}")
            return False

    def get_logs(self) -> dict:
        return self._load_data()

    def set_last_notification(self, topic: str, resource: str, user_id: str | None):
        data = self._load_data()

        data["last_notification"] = {
            "text": f"Tópico: {topic} | Resource: {resource} | User ID: {user_id or '-'}",
            "timestamp": self._now(),
        }

        self._save_data(data)

    def set_last_order(self, order_id: str, item_title: str | None):
        data = self._load_data()

        data["last_order"] = {
            "text": f"ORDER_ID: {order_id} | Item: {item_title or '-'}",
            "timestamp": self._now(),
        }

        self._save_data(data)

    def set_last_shipment(self, shipment_id: str, status: str | None, substatus: str | None):
        data = self._load_data()

        data["last_shipment"] = {
            "text": (
                f"SHIPMENT_ID: {shipment_id} | "
                f"Status: {status or '-'} | "
                f"Substatus: {substatus or '-'}"
            ),
            "timestamp": self._now(),
        }

        self._save_data(data)

    def set_last_label(self, file_path: str):
        data = self._load_data()

        data["last_label"] = {
            "text": f"Etiqueta baixada: {file_path}",
            "timestamp": self._now(),
        }

        self._save_data(data)

    def set_last_print(self, printer_name: str, file_path: str):
        data = self._load_data()

        data["last_print"] = {
            "text": f"Impressora: {printer_name} | Arquivo: {file_path}",
            "timestamp": self._now(),
        }

        self._save_data(data)

    def set_last_error(self, message: str):
        data = self._load_data()

        data["last_error"] = {
            "text": message,
            "timestamp": self._now(),
        }

        self._save_data(data)

    def _now(self) -> str:
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")