from typing import Any

import crescent
from hikari import Intents

from .config import CONFIG
from .database.database import Database


class Minigames(crescent.Bot):
    def __init__(self) -> None:
        super().__init__(
            intents=Intents.ALL_UNPRIVILEGED | Intents.MESSAGE_CONTENT,
            token=CONFIG.discord_token,
        )

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
