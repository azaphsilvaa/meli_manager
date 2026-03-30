from datetime import datetime
from typing import Optional

from core.database import SessionLocal
from models.order import MercadoLivreOrder
from services.account_service import AccountService
from services.meli_order_service import MercadoLivreOrderService


class OrderService:
    def create_or_update_order(
        self,
        ml_order_id: str,
        account_user_id: str | None = None,
        account_nickname: str | None = None,
        ml_pack_id: str | None = None,
        ml_shipment_id: str | None = None,
        buyer_nickname: str | None = None,
        buyer_name: str | None = None,
        item_id: str | None = None,
        item_title: str | None = None,
        item_quantity: int = 1,
        item_price: float | None = None,
        total_amount: float | None = None,
        order_status: str | None = None,
        shipping_status: str | None = None,
        payment_status: str | None = None,
        tags: str | None = None,
        raw_json: str | None = None,
        created_at_ml: datetime | None = None,
        updated_at_ml: datetime | None = None,
    ) -> MercadoLivreOrder:
        session = SessionLocal()

        try:
            order = (
                session.query(MercadoLivreOrder)
                .filter(MercadoLivreOrder.ml_order_id == ml_order_id)
                .first()
            )

            if order:
                order.account_user_id = account_user_id
                order.account_nickname = account_nickname
                order.ml_pack_id = ml_pack_id
                order.ml_shipment_id = ml_shipment_id
                order.buyer_nickname = buyer_nickname
                order.buyer_name = buyer_name
                order.item_id = item_id
                order.item_title = item_title
                order.item_quantity = item_quantity
                order.item_price = item_price
                order.total_amount = total_amount
                order.order_status = order_status
                order.shipping_status = shipping_status
                order.payment_status = payment_status
                order.tags = tags
                order.raw_json = raw_json
                order.created_at_ml = created_at_ml
                order.updated_at_ml = updated_at_ml
            else:
                order = MercadoLivreOrder(
                    ml_order_id=ml_order_id,
                    account_user_id=account_user_id,
                    account_nickname=account_nickname,
                    ml_pack_id=ml_pack_id,
                    ml_shipment_id=ml_shipment_id,
                    buyer_nickname=buyer_nickname,
                    buyer_name=buyer_name,
                    item_id=item_id,
                    item_title=item_title,
                    item_quantity=item_quantity,
                    item_price=item_price,
                    total_amount=total_amount,
                    order_status=order_status,
                    shipping_status=shipping_status,
                    payment_status=payment_status,
                    tags=tags,
                    raw_json=raw_json,
                    created_at_ml=created_at_ml,
                    updated_at_ml=updated_at_ml,
                )
                session.add(order)

            session.commit()
            session.refresh(order)

            return order

        finally:
            session.close()

    def list_orders(self) -> list[MercadoLivreOrder]:
        session = SessionLocal()

        try:
            return (
                session.query(MercadoLivreOrder)
                .order_by(MercadoLivreOrder.created_at.desc())
                .all()
            )
        finally:
            session.close()

    def get_order_by_ml_id(self, ml_order_id: str) -> Optional[MercadoLivreOrder]:
        session = SessionLocal()

        try:
            return (
                session.query(MercadoLivreOrder)
                .filter(MercadoLivreOrder.ml_order_id == ml_order_id)
                .first()
            )
        finally:
            session.close()

    def delete_order_by_ml_id(self, ml_order_id: str) -> bool:
        session = SessionLocal()

        try:
            order = (
                session.query(MercadoLivreOrder)
                .filter(MercadoLivreOrder.ml_order_id == ml_order_id)
                .first()
            )

            if not order:
                return False

            session.delete(order)
            session.commit()

            return True

        finally:
            session.close()

    def delete_all_orders(self) -> int:
        session = SessionLocal()

        try:
            count = session.query(MercadoLivreOrder).delete()
            session.commit()
            return count
        finally:
            session.close()

    def create_test_order(self) -> MercadoLivreOrder:
        now = datetime.utcnow()
        test_order_id = f"TEST-{int(now.timestamp())}"

        return self.create_or_update_order(
            ml_order_id=test_order_id,
            account_user_id="1717448232",
            account_nickname="Loja Teste Pixel",
            ml_pack_id="PACK-TEST-001",
            ml_shipment_id="SHIP-TEST-001",
            buyer_nickname="comprador_teste",
            buyer_name="João Silva",
            item_id="MLBTEST123",
            item_title="Mouse Gamer RGB Pixel Edition",
            item_quantity=1,
            item_price=199.90,
            total_amount=199.90,
            order_status="paid",
            shipping_status="ready_to_ship",
            payment_status="approved",
            tags="test,pixel,local",
            raw_json='{"source":"local_test"}',
            created_at_ml=now,
            updated_at_ml=now,
        )

    def create_or_update_order_from_webhook_event(self, event_data: dict) -> MercadoLivreOrder | None:
        body = event_data.get("body", {}) or {}

        topic = body.get("topic") or body.get("type") or "unknown"
        resource = body.get("resource") or ""
        user_id = body.get("user_id")

        order_id = self._extract_order_id(resource)

        if not order_id:
            return None

        now = datetime.utcnow()

        return self.create_or_update_order(
            ml_order_id=order_id,
            account_user_id=str(user_id) if user_id is not None else None,
            account_nickname=f"Conta {user_id}" if user_id is not None else None,
            item_title="Venda recebida via webhook",
            item_quantity=1,
            total_amount=None,
            order_status="webhook_received",
            shipping_status="pending_webhook_details",
            payment_status="pending_webhook_details",
            tags=topic,
            raw_json=str(body),
            created_at_ml=now,
            updated_at_ml=now,
        )

    def create_or_update_from_meli_api(self, order_id: str, user_id: str):
        account_service = AccountService()
        meli_service = MercadoLivreOrderService()

        account = account_service.get_account_by_user_id(user_id)

        if not account:
            print(f"Conta não encontrada para user_id {user_id}")
            return None

        order_data = meli_service.get_order(account.access_token, order_id)

        if not order_data:
            print("Não foi possível buscar o pedido real. Salvando versão básica do webhook.")
            return self.create_or_update_order(
                ml_order_id=str(order_id),
                account_user_id=str(user_id),
                account_nickname=account.nickname or f"Conta {user_id}",
                item_title="Venda recebida via webhook",
                item_quantity=1,
                total_amount=None,
                order_status="webhook_received",
                shipping_status="pending_api_lookup",
                payment_status="pending_api_lookup",
                tags="orders_v2,fallback",
                raw_json=f'{{"order_id":"{order_id}","user_id":"{user_id}","source":"fallback_webhook"}}',
                created_at_ml=datetime.utcnow(),
                updated_at_ml=datetime.utcnow(),
            )

        buyer = order_data.get("buyer", {})
        order_items = order_data.get("order_items", [])

        item = order_items[0] if order_items else {}
        item_info = item.get("item", {})

        buyer_name = buyer.get("first_name")
        if buyer.get("last_name"):
            buyer_name = f"{buyer.get('first_name', '')} {buyer.get('last_name', '')}".strip()

        shipping_data = order_data.get("shipping", {}) or {}
        payments = order_data.get("payments", []) or []

        return self.create_or_update_order(
            ml_order_id=str(order_data.get("id")),
            account_user_id=str(user_id),
            account_nickname=account.nickname,
            ml_pack_id=str(order_data.get("pack_id")) if order_data.get("pack_id") is not None else None,
            ml_shipment_id=str(shipping_data.get("id")) if shipping_data.get("id") is not None else None,
            buyer_nickname=buyer.get("nickname"),
            buyer_name=buyer_name,
            item_id=str(item_info.get("id")) if item_info.get("id") is not None else None,
            item_title=item_info.get("title"),
            item_quantity=item.get("quantity", 1),
            item_price=item.get("unit_price"),
            total_amount=order_data.get("total_amount"),
            order_status=order_data.get("status"),
            shipping_status=shipping_data.get("status"),
            payment_status=payments[0].get("status") if payments else None,
            tags="meli_api",
            raw_json=str(order_data),
        )

    def _extract_order_id(self, resource: str) -> str | None:
        if not resource:
            return None

        cleaned_resource = resource.strip("/")
        parts = cleaned_resource.split("/")

        if len(parts) >= 2 and parts[0] in {"orders", "orders_v2"}:
            return parts[1]

        return None