from __future__ import annotations

from typing import Awaitable, Callable

import crescent
import hikari


async def guild_only(ctx: crescent.Context) -> crescent.HookResult:
    if not ctx.guild_id:
        await ctx.respond(
            "This command can only be used inside servers.", ephemeral=True
        )
        must_exit = True
    else:
        must_exit = False

    return crescent.HookResult(exit=must_exit)


def has_guild_perms(
    perms: hikari.Permissions,
) -> Callable[[crescent.Context], Awaitable[crescent.HookResult]]:
    async def check(ctx: crescent.Context) -> crescent.HookResult:
        await guild_only(ctx)
        assert ctx.guild_id is not None
        assert ctx.member is not None
        assert isinstance(member := ctx.member, hikari.InteractionMember)

        guild = ctx.app.cache.get_guild(ctx.guild_id)
        assert guild is not None

        if perms not in member.permissions:
            await ctx.respond(
                "You don't have permission to use this command.",
                ephemeral=True,
            )
            must_exit = True
        else:
            must_exit = False
        return crescent.HookResult(exit=must_exit)

    return check
