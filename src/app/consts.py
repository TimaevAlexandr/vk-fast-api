import os

ADMINS: list[int] = os.getenv("BOT_ADMINS")

GROUP_ID_COEFFICIENT: int = int(2e9)

DB_PATH: str = os.getenv("BOT_DB_PATH")
