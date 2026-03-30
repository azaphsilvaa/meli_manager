from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from core.database import Base


class MercadoLivreAccount(Base):
    __tablename__ = "mercado_livre_accounts"

    id = Column(Integer, primary_key=True, index=True)

    nickname = Column(String(120), nullable=True)
    user_id = Column(String(50), nullable=True, unique=True, index=True)

    account_label = Column(String(120), nullable=True)
    seller_email = Column(String(180), nullable=True)

    custom_name = Column(String(180), nullable=True)
    description = Column(Text, nullable=True)

    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    token_type = Column(String(50), nullable=True)

    token_expires_at = Column(DateTime, nullable=True)
    last_refresh_at = Column(DateTime, nullable=True)

    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )