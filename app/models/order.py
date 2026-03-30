from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from core.database import Base


class MercadoLivreOrder(Base):
    __tablename__ = "mercado_livre_orders"

    id = Column(Integer, primary_key=True, index=True)

    ml_order_id = Column(String(80), unique=True, index=True, nullable=False)
    ml_pack_id = Column(String(80), nullable=True, index=True)
    ml_shipment_id = Column(String(80), nullable=True, index=True)

    account_user_id = Column(String(50), nullable=True, index=True)
    account_nickname = Column(String(120), nullable=True)

    buyer_nickname = Column(String(120), nullable=True)
    buyer_name = Column(String(180), nullable=True)

    item_id = Column(String(80), nullable=True)
    item_title = Column(String(255), nullable=True)
    item_quantity = Column(Integer, default=1)
    item_price = Column(Float, nullable=True)

    total_amount = Column(Float, nullable=True)

    order_status = Column(String(80), nullable=True)
    shipping_status = Column(String(80), nullable=True)
    payment_status = Column(String(80), nullable=True)

    tags = Column(Text, nullable=True)
    raw_json = Column(Text, nullable=True)

    created_at_ml = Column(DateTime, nullable=True)
    updated_at_ml = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )