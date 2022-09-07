from __future__ import annotations

import random

import crescent

from ._checks import guild_only

plugin = crescent.Plugin(command_hooks=[guild_only])


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

EMOJIFY_MAP = {
    k: f":{v}:"
    for k, v in {
        **{
            letter: f"regional_indicator_{letter}"
            for letter in "abcdefghijklmnopqrstuvwxyz"
        },
        "1": "one",
        "2": "two",
        "3": "three",
        "4": "four",
        "5": "five",
        "6": "six",
        "7": "seven",
        "8": "eight",
        "9": "nine",
        "?": "grey_question",
        "!": "grey_exclamation",
    }.items()
}


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


@plugin.include
@crescent.command(name="emojify", description="Send text as emojis.")
class Emojify:
    text = crescent.option(str, "The text to emojify.")
    hide = crescent.option(bool, "Whether to hide the result.", default=False)

    async def callback(self, ctx: crescent.Context) -> None:
        new_string = "".join(EMOJIFY_MAP.get(char, char) for char in self.text)
        if len(new_string) > 2_000:
            await ctx.respond(
                "The resulting text is too long.", ephemeral=True
            )
        else:
            await ctx.respond(new_string, ephemeral=self.hide)
