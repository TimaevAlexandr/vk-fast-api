import os

# SYSTEM SETTINGS
SENTRY_DSN_URL: str = os.getenv("SENTRY_DSN_URL", "")
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "local")

# APP SETTINGS
ADMINS: list[int] = list(map(int, os.getenv("BOT_ADMINS", "").split(",")))

# VK SETTINGS
GROUP_ID: str = os.getenv("BOT_GROUP_ID", "")
CONFIRMATION_TOKEN: str = os.getenv("BOT_CONFIRMATION_TOKEN", "")

# DB
DB_PATH: str = os.getenv("DB_PATH", "")

# CONSTANTS
GROUP_ID_COEFFICIENT: int = int(2e9)
