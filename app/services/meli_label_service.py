import os

import requests


class MercadoLivreLabelService:
    BASE_URL = "https://api.mercadolibre.com"

    def download_label(self, access_token: str, shipment_id: str) -> str | None:
        url = f"{self.BASE_URL}/shipment_labels?shipment_ids={shipment_id}&response_type=pdf"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "accept": "application/pdf",
        }

        response = requests.get(url, headers=headers, timeout=60)

        if response.status_code != 200:
            print(f"Erro ao baixar etiqueta {shipment_id}: {response.status_code}")
            print(response.text)
            return None

        os.makedirs("data/labels", exist_ok=True)

        file_path = os.path.join("data", "labels", f"label_{shipment_id}.pdf")

        with open(file_path, "wb") as pdf_file:
            pdf_file.write(response.content)

        print(f"Etiqueta salva em: {file_path}")
        return file_path