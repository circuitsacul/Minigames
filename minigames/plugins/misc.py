from __future__ import annotations

import random

import crescent

from ._checks import guild_only

plugin = crescent.Plugin("misc", [guild_only])


MAGIC_8BALL_RESPONSES = [
    "It is certain.",
    "It is decidedly so.",
    "Without a doubt.",
    "Probably not.",
    "Yes.",
    "No.",
    "Maybe.",
    "I don't know.",
    "Ask again later.",
    "Better not tell you now.",
    "Certainly not.",
    "I don't think so.",
]


@plugin.include
@crescent.command(name="8ball", description="Ask the magic 8ball a question.")
class Magic8Ball:
    question = crescent.option(str, "The question.")

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.respond(
            MAGIC_8BALL_RESPONSES[
                random.randint(0, len(MAGIC_8BALL_RESPONSES) - 1)
            ]
        )
