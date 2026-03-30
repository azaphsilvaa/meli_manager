from __future__ import annotations

import secrets
import urllib.parse
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import requests

from config.settings import settings


@dataclass
class OAuthTokenData:
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user_id: str


class MercadoLivreAuthService:
    def __init__(self):
        self.client_id = settings.MERCADO_LIVRE_CLIENT_ID
        self.client_secret = settings.MERCADO_LIVRE_CLIENT_SECRET
        self.redirect_uri = settings.MERCADO_LIVRE_REDIRECT_URI
        self.auth_url = settings.MERCADO_LIVRE_AUTH_URL
        self.api_base_url = settings.MERCADO_LIVRE_BASE_URL
        self.token_url = f"{self.api_base_url}/oauth/token"
        self.me_url = f"{self.api_base_url}/users/me"

    def generate_state(self) -> str:
        return secrets.token_urlsafe(32)

    def build_authorization_url(self, state: str) -> str:
        query_params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": state,
        }

        return f"{self.auth_url}?{urllib.parse.urlencode(query_params)}"

    def exchange_code_for_token(self, code: str) -> OAuthTokenData:
        payload = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
        }

        response = requests.post(
            self.token_url,
            headers={
                "accept": "application/json",
                "content-type": "application/x-www-form-urlencoded",
            },
            data=payload,
            timeout=30,
        )

        self._raise_for_status(response)

        data = response.json()

        return OAuthTokenData(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            token_type=data.get("token_type", "bearer"),
            expires_in=int(data["expires_in"]),
            user_id=str(data["user_id"]),
        )

    def refresh_access_token(self, refresh_token: str) -> OAuthTokenData:
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
        }

        response = requests.post(
            self.token_url,
            headers={
                "accept": "application/json",
                "content-type": "application/x-www-form-urlencoded",
            },
            data=payload,
            timeout=30,
        )

        self._raise_for_status(response)

        data = response.json()

        return OAuthTokenData(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            token_type=data.get("token_type", "bearer"),
            expires_in=int(data["expires_in"]),
            user_id=str(data["user_id"]),
        )

    def get_current_user_profile(self, access_token: str) -> dict[str, Any]:
        response = requests.get(
            self.me_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "accept": "application/json",
            },
            timeout=30,
        )

        self._raise_for_status(response)
        return response.json()

    def calculate_token_expires_at(self, expires_in: int) -> datetime:
        return datetime.now(UTC) + timedelta(seconds=expires_in)

    def validate_environment(self) -> tuple[bool, str]:
        if not self.client_id:
            return False, "MERCADO_LIVRE_CLIENT_ID não configurado no .env."

        if not self.client_secret:
            return False, "MERCADO_LIVRE_CLIENT_SECRET não configurado no .env."

        if not self.redirect_uri:
            return False, "MERCADO_LIVRE_REDIRECT_URI não configurado no .env."

        return True, "Configuração OAuth válida."

    def _raise_for_status(self, response: requests.Response) -> None:
        if response.ok:
            return

        try:
            error_data: dict[str, Any] = response.json()
            error_message = (
                error_data.get("message")
                or error_data.get("error_description")
                or str(error_data)
            )
        except Exception:
            error_message = response.text

        raise Exception(f"Erro Mercado Livre OAuth/API ({response.status_code}): {error_message}")