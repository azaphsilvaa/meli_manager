from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from core.database import Base


class MercadoLivreShipment(Base):
    __tablename__ = "mercado_livre_shipments"

    id = Column(Integer, primary_key=True, index=True)

    ml_shipment_id = Column(String(80), unique=True, index=True, nullable=False)
    ml_order_id = Column(String(80), nullable=True, index=True)
    account_user_id = Column(String(50), nullable=True, index=True)

    shipping_mode = Column(String(80), nullable=True)
    shipping_status = Column(String(80), nullable=True)
    shipping_substatus = Column(String(120), nullable=True)

    logistic_type = Column(String(80), nullable=True)
    picking_type = Column(String(80), nullable=True)

    receiver_name = Column(String(180), nullable=True)
    receiver_address = Column(Text, nullable=True)

    cost = Column(Float, nullable=True)
    currency_id = Column(String(20), nullable=True)

    tracking_number = Column(String(120), nullable=True)
    tracking_method = Column(String(120), nullable=True)

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