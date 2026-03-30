import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    APP_NAME = "SOFTWARE ML"
    APP_ENV = os.getenv("APP_ENV", "development")
    APP_DEBUG = os.getenv("APP_DEBUG", "true").lower() == "true"

    MERCADO_LIVRE_CLIENT_ID = os.getenv("MERCADO_LIVRE_CLIENT_ID", "")
    MERCADO_LIVRE_CLIENT_SECRET = os.getenv("MERCADO_LIVRE_CLIENT_SECRET", "")
    MERCADO_LIVRE_REDIRECT_URI = os.getenv("MERCADO_LIVRE_REDIRECT_URI", "")
    MERCADO_LIVRE_BASE_URL = os.getenv("MERCADO_LIVRE_BASE_URL", "https://api.mercadolibre.com")
    MERCADO_LIVRE_AUTH_URL = os.getenv("MERCADO_LIVRE_AUTH_URL", "https://auth.mercadolivre.com.br/authorization")

    DATA_DIR = os.getenv("DATA_DIR", "data")
    LABELS_DIR = os.getenv("LABELS_DIR", "data/labels")
    TEMP_DIR = os.getenv("TEMP_DIR", "data/temp")
    DB_PATH = os.getenv("DB_PATH", "data/db/software_ml.db")


settings = Settings()