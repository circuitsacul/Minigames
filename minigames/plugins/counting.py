from __future__ import annotations

from contextlib import suppress

import asyncpg
import cachetools
import crescent
import hikari

from minigames.database.models.counting import CountingFlags, CountingGame
from minigames.undefined import UNDEF

from ._checks import guild_only, has_guild_perms

COUNT_CHANNEL_CACHE: cachetools.LFUCache[
    int, CountingGame | None
] = cachetools.LFUCache(maxsize=100)


async def get_counting_channel(channel_id: int) -> CountingGame | None:
    if (
        game := COUNT_CHANNEL_CACHE.get(channel_id, hikari.UNDEFINED)
    ) is not hikari.UNDEFINED:
        return game
    game = await CountingGame.exists(channel_id=channel_id)
    COUNT_CHANNEL_CACHE[channel_id] = game
    return game


def get_number(message: str) -> int | None:
    with suppress(ValueError):
        return int(message.replace(",", ""))

    return None


plugin = crescent.Plugin()


# events
@plugin.include
@crescent.event
async def on_message(event: hikari.GuildMessageCreateEvent) -> None:
    if event.message.author.is_bot:
        return
    if (game := await get_counting_channel(event.channel_id)) is None:
        return

    number = (
        get_number(event.message.content) if event.message.content else None
    )
    if number is None:
        if CountingFlags.REMOVE_NON_NUMBERS in game.flags:
            with suppress(hikari.ForbiddenError, hikari.NotFoundError):
                await event.message.delete()
        return

    invalid_reason: str | None = None

    if (
        CountingFlags.ALLOW_DOUBLE_COUNT not in game.flags
        and game.last_counter == event.message.author.id
    ):
        invalid_reason = "You can't count twice in a row."
    if number != game.current_number:
        invalid_reason = (
            "Incorrect number! The correct number was "
            f"`{game.current_number}`."
        )

    if invalid_reason:
        await event.message.add_reaction("❌")
        if CountingFlags.RESET_ON_INCORRECT in game.flags:
            await event.message.respond(
                f"{invalid_reason} The game has been reset to 1.", reply=True
            )
            game.current_number = 1
            game.last_counter = None
            await game.save()
        else:
            await event.message.respond(invalid_reason, reply=True)
        return
    game.current_number += 1
    game.last_counter = event.message.author.id
    await game.save()
    await event.message.add_reaction("✅")


# commands
group = crescent.Group(
    "counting", "Counting-related commands.", hooks=[guild_only]
)


@plugin.include
@group.child
@crescent.hook(has_guild_perms(hikari.Permissions.MANAGE_MESSAGES))
@crescent.command(name="start", description="Create a new counting game.")
class NewCountingGame:
    async def callback(self, ctx: crescent.Context) -> None:
        assert ctx.guild_id
        try:
            await CountingGame(
                guild_id=ctx.guild_id, channel_id=ctx.channel_id
            ).create()
        except asyncpg.UniqueViolationError:
            await ctx.respond(
                "A counting game is already running in this channel."
            )
            return

        COUNT_CHANNEL_CACHE.pop(ctx.channel_id, None)
        await ctx.respond("Counting game started!")


@plugin.include
@group.child
@crescent.hook(has_guild_perms(hikari.Permissions.MANAGE_MESSAGES))
@crescent.command(name="stop", description="Delete a counting game.")
class StopCountingGame:
    async def callback(self, ctx: crescent.Context) -> None:
        assert ctx.guild_id
        if (game := await get_counting_channel(ctx.channel_id)) is None:
            await ctx.respond(
                "There is no counting game running in this channel."
            )
            return

        COUNT_CHANNEL_CACHE.pop(ctx.channel_id, None)
        await game.delete()
        await ctx.respond("Counting game stopped.")


@plugin.include
@group.child
@crescent.hook(has_guild_perms(hikari.Permissions.MANAGE_MESSAGES))
@crescent.command(name="edit", description="Edit a counting game.")
class EditCountingGame:
    allow_double_count = crescent.option(
        bool,
        "Whether to allow someone to count multiple times in a row.",
        name="allow-double-count",
        default=UNDEF.UNDEF,
    )
    reset_on_incorrect = crescent.option(
        bool,
        "Whether to reset the game when an incorrect number is typed.",
        name="reset-on-incorrect",
        default=UNDEF.UNDEF,
    )
    remove_non_numbers = crescent.option(
        bool,
        "Whether to remove messages that aren't numbers.",
        name="remove-non-numbers",
        default=UNDEF.UNDEF,
    )

    async def callback(self, ctx: crescent.Context) -> None:
        assert ctx.guild_id

        if (game := await get_counting_channel(ctx.channel_id)) is None:
            await ctx.respond(
                "There is no counting game running in this channel."
            )
            return

        flags = game.flags

        def update(bool_val: UNDEF | bool, flag: CountingFlags) -> None:
            nonlocal flags
            if bool_val is not UNDEF.UNDEF:
                flags = flags | flag if bool_val else flags & ~flag

        update(self.allow_double_count, CountingFlags.ALLOW_DOUBLE_COUNT)
        update(self.reset_on_incorrect, CountingFlags.RESET_ON_INCORRECT)
        update(self.remove_non_numbers, CountingFlags.REMOVE_NON_NUMBERS)

        if flags == game.flags:
            await ctx.respond("No changes were made.")
            return
        game.flags = flags
        await game.save()
        await ctx.respond("Counting game updated.")


@plugin.include
@group.child
@crescent.hook(has_guild_perms(hikari.Permissions.MANAGE_MESSAGES))
@crescent.command(name="set", description="Set the current number.")
class SetCurrentNumber:
    number = crescent.option(
        int, "The number to set the current number to.", min_value=0
    )

    async def callback(self, ctx: crescent.Context) -> None:
        assert ctx.guild_id

        if (game := await get_counting_channel(ctx.channel_id)) is None:
            await ctx.respond(
                "There is no counting game running in this channel."
            )
            return

        game.current_number = self.number
        await game.save()
        await ctx.respond("Current number set.")


@plugin.include
@group.child
@crescent.command(name="next", description="Show the next number.")
class CurrentNumber:
    async def callback(self, ctx: crescent.Context) -> None:
        assert ctx.guild_id
        if (game := await get_counting_channel(ctx.channel_id)) is None:
            await ctx.respond(
                "There is no counting game running in this channel."
            )
            return

        await ctx.respond(f"The next number is `{game.current_number}`.")


@plugin.include
@group.child
@crescent.command(name="list", description="List all counting channel.")
class ListCountingChannel:
    async def callback(self, ctx: crescent.Context) -> None:
        assert ctx.guild_id
        if not (
            channels := await CountingGame.fetch_query()
            .where(guild_id=ctx.guild_id)
            .fetchmany()
        ):
            await ctx.respond("There are no counting channels.")
            return

        await ctx.respond(
            "Counting channels:\n"
            + "\n".join(
                f"<#{channel.channel_id}>: `{channel.current_number}`"
                for channel in channels
            )
        )


@plugin.include
@group.child
@crescent.command(
    name="view", description="View the settings for a counting channel."
)
class ViewCountingChannel:
    async def callback(self, ctx: crescent.Context) -> None:
        assert ctx.guild_id
        if (game := await get_counting_channel(ctx.channel_id)) is None:
            await ctx.respond(
                "There is no counting game running in this channel."
            )
            return

        await ctx.respond(
            "Counting settings:\n"
            + "\n".join(
                f"`{flag.name.lower().replace('_', '-')}`: "
                f"`{'True' if flag in game.flags else 'False'}`"
                for flag in CountingFlags
                if flag.name is not None
            )
        )
