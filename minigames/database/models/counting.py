from enum import IntFlag

from apgorm import IntEFConverter, Model, types

from minigames.database.converters import DecimalC, NullDecimalC


class CountingFlags(IntFlag):
    ALLOW_DOUBLE_COUNT = 1 << 0
    RESET_ON_INCORRECT = 1 << 1


class CountingGame(Model):
    guild_id = types.Numeric().field().with_converter(DecimalC)
    channel_id = types.Numeric().field().with_converter(DecimalC)
    current_number = types.BigInt().field(default=1)
    last_counter = types.Numeric().nullablefield().with_converter(NullDecimalC)

    flags = (
        types.SmallInt()
        .field(default=0)
        .with_converter(IntEFConverter(CountingFlags))
    )

    primary_key = (channel_id,)
