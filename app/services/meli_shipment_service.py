import requests


class MercadoLivreShipmentService:
    BASE_URL = "https://api.mercadolibre.com"

    def get_shipment(self, access_token: str, shipment_id: str) -> dict | None:
        url = f"{self.BASE_URL}/shipments/{shipment_id}"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "accept": "application/json",
        }

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code != 200:
            print(f"Erro ao buscar shipment {shipment_id}: {response.status_code}")
            print(response.text)
            return None

        return response.json()