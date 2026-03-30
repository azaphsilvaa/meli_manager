from datetime import datetime
from typing import Optional

from core.database import SessionLocal
from models.account import MercadoLivreAccount


class AccountService:
    def create_or_update_account(
        self,
        user_id: str,
        access_token: str,
        refresh_token: str,
        token_type: str = "bearer",
        nickname: str | None = None,
        account_label: str | None = None,
        seller_email: str | None = None,
        token_expires_at: datetime | None = None,
        is_active: bool = True,
    ) -> MercadoLivreAccount:
        session = SessionLocal()

        try:
            account = (
                session.query(MercadoLivreAccount)
                .filter(MercadoLivreAccount.user_id == user_id)
                .first()
            )

            if account:
                account.access_token = access_token
                account.refresh_token = refresh_token
                account.token_type = token_type
                account.nickname = nickname
                account.account_label = account_label
                account.seller_email = seller_email
                account.token_expires_at = token_expires_at
                account.last_refresh_at = datetime.utcnow()
                account.is_active = is_active
            else:
                account = MercadoLivreAccount(
                    user_id=user_id,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_type=token_type,
                    nickname=nickname,
                    account_label=account_label,
                    seller_email=seller_email,
                    token_expires_at=token_expires_at,
                    last_refresh_at=datetime.utcnow(),
                    is_active=is_active,
                    is_default=False,
                )
                session.add(account)

            session.commit()
            session.refresh(account)

            return account

        finally:
            session.close()

    def list_accounts(self) -> list[MercadoLivreAccount]:
        session = SessionLocal()

        try:
            return (
                session.query(MercadoLivreAccount)
                .order_by(MercadoLivreAccount.id.asc())
                .all()
            )
        finally:
            session.close()

    def list_active_accounts(self) -> list[MercadoLivreAccount]:
        session = SessionLocal()

        try:
            return (
                session.query(MercadoLivreAccount)
                .filter(MercadoLivreAccount.is_active.is_(True))
                .order_by(MercadoLivreAccount.id.asc())
                .all()
            )
        finally:
            session.close()

    def get_account_by_user_id(self, user_id: str) -> Optional[MercadoLivreAccount]:
        session = SessionLocal()

        try:
            return (
                session.query(MercadoLivreAccount)
                .filter(MercadoLivreAccount.user_id == user_id)
                .first()
            )
        finally:
            session.close()

    def get_account_by_id(self, account_id: int) -> Optional[MercadoLivreAccount]:
        session = SessionLocal()

        try:
            return (
                session.query(MercadoLivreAccount)
                .filter(MercadoLivreAccount.id == account_id)
                .first()
            )
        finally:
            session.close()

    def set_default_account(self, account_id: int) -> bool:
        session = SessionLocal()

        try:
            target_account = (
                session.query(MercadoLivreAccount)
                .filter(MercadoLivreAccount.id == account_id)
                .first()
            )

            if not target_account:
                return False

            all_accounts = session.query(MercadoLivreAccount).all()

            for account in all_accounts:
                account.is_default = account.id == account_id

            session.commit()
            return True

        finally:
            session.close()

    def set_account_active_status(self, account_id: int, is_active: bool) -> bool:
        session = SessionLocal()

        try:
            account = (
                session.query(MercadoLivreAccount)
                .filter(MercadoLivreAccount.id == account_id)
                .first()
            )

            if not account:
                return False

            account.is_active = is_active
            session.commit()

            return True

        finally:
            session.close()

    def update_account_tokens(
        self,
        account_id: int,
        access_token: str,
        refresh_token: str,
        token_type: str,
        token_expires_at: datetime | None,
    ) -> bool:
        session = SessionLocal()

        try:
            account = (
                session.query(MercadoLivreAccount)
                .filter(MercadoLivreAccount.id == account_id)
                .first()
            )

            if not account:
                return False

            account.access_token = access_token
            account.refresh_token = refresh_token
            account.token_type = token_type
            account.token_expires_at = token_expires_at
            account.last_refresh_at = datetime.utcnow()

            session.commit()
            return True

        finally:
            session.close()

    def update_account_profile(
        self,
        account_id: int,
        nickname: str | None = None,
        seller_email: str | None = None,
        account_label: str | None = None,
    ) -> bool:
        session = SessionLocal()

        try:
            account = (
                session.query(MercadoLivreAccount)
                .filter(MercadoLivreAccount.id == account_id)
                .first()
            )

            if not account:
                return False

            account.nickname = nickname
            account.seller_email = seller_email
            account.account_label = account_label

            session.commit()
            return True

        finally:
            session.close()

    def update_custom_fields(
        self,
        account_id: int,
        custom_name: str | None,
        description: str | None,
    ) -> bool:
        session = SessionLocal()

        try:
            account = (
                session.query(MercadoLivreAccount)
                .filter(MercadoLivreAccount.id == account_id)
                .first()
            )

            if not account:
                return False

            account.custom_name = custom_name.strip() if custom_name else None
            account.description = description.strip() if description else None

            session.commit()
            return True

        finally:
            session.close()

    def delete_account(self, account_id: int) -> bool:
        session = SessionLocal()

        try:
            account = (
                session.query(MercadoLivreAccount)
                .filter(MercadoLivreAccount.id == account_id)
                .first()
            )

            if not account:
                return False

            session.delete(account)
            session.commit()

            return True

        finally:
            session.close()