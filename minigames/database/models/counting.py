from enum import IntFlag

from apgorm import ForeignKey, IntEFConverter, Model, types

from minigames.database.converters import DecimalC, NullDecimalC


class CountingFlags(IntFlag):
    ALLOW_DOUBLE_COUNT = 1 << 0
    RESET_ON_INCORRECT = 1 << 1
    REMOVE_NON_NUMBERS = 1 << 2


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


class CountingUser(Model):
    game_channel_id = types.Numeric().field().with_converter(DecimalC)
    user_id = types.Numeric().field().with_converter(DecimalC)

    total_numbers_counted = types.Int().field(default=0)

    game_channel_id_fk = ForeignKey(game_channel_id, CountingGame.channel_id)

    primary_key = (game_channel_id, user_id)
