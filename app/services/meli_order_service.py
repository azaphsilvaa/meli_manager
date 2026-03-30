import requests


class MercadoLivreOrderService:
    BASE_URL = "https://api.mercadolibre.com"

    def get_order(self, access_token: str, order_id: str) -> dict | None:
        url = f"{self.BASE_URL}/orders/{order_id}"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "accept": "application/json",
        }

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code != 200:
            print(f"Erro ao buscar pedido {order_id}: {response.status_code}")
            print(response.text)
            return None

        return response.json()

    def search_orders_by_seller(self, access_token: str, seller_id: str) -> dict | None:
        url = f"{self.BASE_URL}/orders/search?seller={seller_id}"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "accept": "application/json",
        }

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code != 200:
            print(f"Erro ao buscar pedidos do seller {seller_id}: {response.status_code}")
            print(response.text)
            return None

        return response.json()