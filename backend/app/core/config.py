
import os
from pathlib import Path
from dotenv import load_dotenv

# Load backend/.env
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_FILE)


class Settings:
    APP_NAME: str = "Researchify"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://researchify:researchify_dev_password@localhost:5432/researchify",
    )

    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "CHANGE_THIS_TO_A_RANDOM_SECRET_KEY",
    )

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()
