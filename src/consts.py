import os

ADMINS: list[int] = list(map(int, os.getenv("BOT_ADMINS", "").split(",")))

GROUP_ID_COEFFICIENT: int = int(2e9)

DB_PATH: str = os.getenv("DB_PATH", "")

GROUP_ID: str = os.getenv("BOT_GROUP_ID", "")

CONFIRMATION_TOKEN: str = os.getenv("BOT_CONFIRMATION_TOKEN", "")
