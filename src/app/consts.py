import os

ADMINS: list[int] = list(
    map(int, os.getenv('BOT_ADMINS', '').split())
)

GROUP_ID_COEFFICIENT: int = int(2e9)

DB_PATH: str | None = os.getenv('DB_PATH')
