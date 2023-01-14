from typing import Any

import crescent

from .config import CONFIG
from .database.database import Database


class Minigames(crescent.Bot):
    def __init__(self) -> None:
        super().__init__(CONFIG.discord_token)

        self.database = Database()
        self.plugins.load_folder("minigames.plugins")

    async def start(self, **kwargs: Any) -> None:
        await self.database.connect(
            host=CONFIG.database_host,
            user=CONFIG.database_user,
            password=CONFIG.database_password,
            database=CONFIG.database_name,
        )
        await super().start(**kwargs)
