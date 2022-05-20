import apgorm

from .models.counting import CountingGame


class Database(apgorm.Database):
    def __init__(self):
        super().__init__("minigames/database/migrations")

    async def connect(self, **connect_kwargs) -> None:
        await super().connect(**connect_kwargs)
        if self.must_create_migrations():
            raise Exception("There are uncreated migrations.")
        if await self.must_apply_migrations():
            print("Applying migrations...")
            await self.apply_migrations()

    counting_channels = CountingGame
