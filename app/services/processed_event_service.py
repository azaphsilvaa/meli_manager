import json
import os
import time


class ProcessedEventService:
    FILE_PATH = os.path.join("data", "processed_events.json")

    def __init__(self):
        os.makedirs("data", exist_ok=True)

        if not os.path.exists(self.FILE_PATH):
            self._save_data(
                {
                    "events": {},
                    "printed_shipments": {},
                }
            )

    def _load_data(self) -> dict:
        try:
            with open(self.FILE_PATH, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return {
                "events": {},
                "printed_shipments": {},
            }

    def _save_data(self, data: dict):
        with open(self.FILE_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def build_event_key(self, topic: str, resource: str, user_id: str) -> str:
        return f"{topic}|{resource}|{user_id}"

    def is_event_processed(self, topic: str, resource: str, user_id: str) -> bool:
        data = self._load_data()
        event_key = self.build_event_key(topic, resource, user_id)

        return event_key in data.get("events", {})

    def mark_event_processed(self, topic: str, resource: str, user_id: str):
        data = self._load_data()
        event_key = self.build_event_key(topic, resource, user_id)

        data.setdefault("events", {})
        data["events"][event_key] = {
            "topic": topic,
            "resource": resource,
            "user_id": user_id,
            "timestamp": int(time.time()),
        }

        self._save_data(data)

    def is_shipment_already_printed(self, shipment_id: str) -> bool:
        data = self._load_data()
        return str(shipment_id) in data.get("printed_shipments", {})

    def mark_shipment_printed(self, shipment_id: str, file_path: str = ""):
        data = self._load_data()

        data.setdefault("printed_shipments", {})
        data["printed_shipments"][str(shipment_id)] = {
            "shipment_id": str(shipment_id),
            "file_path": file_path,
            "timestamp": int(time.time()),
        }

        self._save_data(data)

    def clear_old_events(self, max_age_seconds: int = 86400):
        data = self._load_data()
        now = int(time.time())

        filtered_events = {}

        for event_key, item in data.get("events", {}).items():
            timestamp = int(item.get("timestamp", 0))

            if now - timestamp <= max_age_seconds:
                filtered_events[event_key] = item

        data["events"] = filtered_events
        self._save_data(data)