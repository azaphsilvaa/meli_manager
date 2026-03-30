from datetime import datetime
from typing import Optional

from core.database import SessionLocal
from models.shipment import MercadoLivreShipment
from services.account_service import AccountService
from services.meli_shipment_service import MercadoLivreShipmentService


class ShipmentService:
    def create_or_update_shipment(
        self,
        ml_shipment_id: str,
        ml_order_id: str | None = None,
        account_user_id: str | None = None,
        shipping_mode: str | None = None,
        shipping_status: str | None = None,
        shipping_substatus: str | None = None,
        logistic_type: str | None = None,
        picking_type: str | None = None,
        receiver_name: str | None = None,
        receiver_address: str | None = None,
        cost: float | None = None,
        currency_id: str | None = None,
        tracking_number: str | None = None,
        tracking_method: str | None = None,
        tags: str | None = None,
        raw_json: str | None = None,
        created_at_ml: datetime | None = None,
        updated_at_ml: datetime | None = None,
    ) -> MercadoLivreShipment:
        session = SessionLocal()

        try:
            shipment = (
                session.query(MercadoLivreShipment)
                .filter(MercadoLivreShipment.ml_shipment_id == ml_shipment_id)
                .first()
            )

            if shipment:
                shipment.ml_order_id = ml_order_id
                shipment.account_user_id = account_user_id
                shipment.shipping_mode = shipping_mode
                shipment.shipping_status = shipping_status
                shipment.shipping_substatus = shipping_substatus
                shipment.logistic_type = logistic_type
                shipment.picking_type = picking_type
                shipment.receiver_name = receiver_name
                shipment.receiver_address = receiver_address
                shipment.cost = cost
                shipment.currency_id = currency_id
                shipment.tracking_number = tracking_number
                shipment.tracking_method = tracking_method
                shipment.tags = tags
                shipment.raw_json = raw_json
                shipment.created_at_ml = created_at_ml
                shipment.updated_at_ml = updated_at_ml
            else:
                shipment = MercadoLivreShipment(
                    ml_shipment_id=ml_shipment_id,
                    ml_order_id=ml_order_id,
                    account_user_id=account_user_id,
                    shipping_mode=shipping_mode,
                    shipping_status=shipping_status,
                    shipping_substatus=shipping_substatus,
                    logistic_type=logistic_type,
                    picking_type=picking_type,
                    receiver_name=receiver_name,
                    receiver_address=receiver_address,
                    cost=cost,
                    currency_id=currency_id,
                    tracking_number=tracking_number,
                    tracking_method=tracking_method,
                    tags=tags,
                    raw_json=raw_json,
                    created_at_ml=created_at_ml,
                    updated_at_ml=updated_at_ml,
                )
                session.add(shipment)

            session.commit()
            session.refresh(shipment)

            return shipment

        finally:
            session.close()

    def get_shipment_by_ml_id(self, ml_shipment_id: str) -> Optional[MercadoLivreShipment]:
        session = SessionLocal()

        try:
            return (
                session.query(MercadoLivreShipment)
                .filter(MercadoLivreShipment.ml_shipment_id == ml_shipment_id)
                .first()
            )
        finally:
            session.close()

    def list_shipments(self) -> list[MercadoLivreShipment]:
        session = SessionLocal()

        try:
            return (
                session.query(MercadoLivreShipment)
                .order_by(MercadoLivreShipment.created_at.desc())
                .all()
            )
        finally:
            session.close()

    def create_test_shipment(self) -> MercadoLivreShipment:
        now = datetime.utcnow()

        return self.create_or_update_shipment(
            ml_shipment_id=f"SHIP-TEST-{int(now.timestamp())}",
            ml_order_id=f"ORDER-TEST-{int(now.timestamp())}",
            account_user_id="1717448232",
            shipping_mode="me2",
            shipping_status="ready_to_ship",
            shipping_substatus="ready_to_print",
            logistic_type="drop_off",
            picking_type="cross_docking",
            receiver_name="João Silva",
            receiver_address="Rua Teste, 123 - São Paulo/SP",
            cost=25.50,
            currency_id="BRL",
            tracking_number="TRACK123456789",
            tracking_method="Correios",
            tags="test,shipment",
            raw_json='{"source":"local_test_shipment"}',
            created_at_ml=now,
            updated_at_ml=now,
        )

    def create_or_update_from_meli_api(
        self,
        shipment_id: str,
        user_id: str,
        ml_order_id: str | None = None,
    ) -> MercadoLivreShipment | None:
        account_service = AccountService()
        meli_shipment_service = MercadoLivreShipmentService()

        account = account_service.get_account_by_user_id(user_id)

        if not account:
            print(f"Conta não encontrada para user_id {user_id}")
            return None

        shipment_data = meli_shipment_service.get_shipment(
            access_token=account.access_token,
            shipment_id=shipment_id,
        )

        if not shipment_data:
            print(f"Não foi possível buscar shipment real {shipment_id}.")
            return None

        receiver_address_data = shipment_data.get("receiver_address", {}) or {}
        receiver_name = receiver_address_data.get("receiver_name")

        receiver_address_parts = [
            receiver_address_data.get("street_name"),
            str(receiver_address_data.get("street_number"))
            if receiver_address_data.get("street_number") is not None
            else None,
            receiver_address_data.get("city", {}).get("name")
            if receiver_address_data.get("city")
            else None,
            receiver_address_data.get("state", {}).get("name")
            if receiver_address_data.get("state")
            else None,
        ]
        receiver_address = ", ".join([part for part in receiver_address_parts if part])

        shipment_order_id = ml_order_id

        if not shipment_order_id:
            order_data = shipment_data.get("order", {}) or {}
            if order_data.get("id") is not None:
                shipment_order_id = str(order_data.get("id"))

        return self.create_or_update_shipment(
            ml_shipment_id=str(shipment_data.get("id")),
            ml_order_id=shipment_order_id,
            account_user_id=str(user_id),
            shipping_mode=shipment_data.get("mode"),
            shipping_status=shipment_data.get("status"),
            shipping_substatus=shipment_data.get("substatus"),
            logistic_type=shipment_data.get("logistic_type"),
            picking_type=shipment_data.get("picking_type"),
            receiver_name=receiver_name,
            receiver_address=receiver_address or None,
            cost=shipment_data.get("cost"),
            currency_id=shipment_data.get("currency_id"),
            tracking_number=shipment_data.get("tracking_number"),
            tracking_method=shipment_data.get("tracking_method"),
            tags="meli_shipment_api",
            raw_json=str(shipment_data),
        )