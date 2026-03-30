import os
from datetime import datetime


class LabelFileService:
    LABELS_DIR = os.path.join("data", "labels")

    def list_labels(self) -> list[dict]:
        os.makedirs(self.LABELS_DIR, exist_ok=True)

        labels = []

        for file_name in os.listdir(self.LABELS_DIR):
            if not file_name.lower().endswith(".pdf"):
                continue

            file_path = os.path.join(self.LABELS_DIR, file_name)

            if not os.path.isfile(file_path):
                continue

            stat = os.stat(file_path)

            labels.append(
                {
                    "file_name": file_name,
                    "file_path": file_path,
                    "modified_at": datetime.fromtimestamp(stat.st_mtime),
                    "size_bytes": stat.st_size,
                }
            )

        labels.sort(key=lambda item: item["modified_at"], reverse=True)
        return labels

    def delete_label(self, file_path: str) -> bool:
        try:
            if not os.path.exists(file_path):
                return False

            os.remove(file_path)
            return True

        except Exception as error:
            print(f"Erro ao remover etiqueta: {error}")
            return False