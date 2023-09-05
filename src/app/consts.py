import os

ADMINS: list[int] | None = os.getenv("BOT_ADMINS")

GROUP_ID_COEFFICIENT: int = int(2e9)

DB_PATH: str | None = os.getenv("DB_PATH")
