from __future__ import annotations

from decimal import Decimal

import apgorm


class DecimalC(apgorm.Converter[Decimal, int]):
    def from_stored(self, value: Decimal) -> int:
        return int(value)

    def to_stored(self, value: int) -> Decimal:
        return Decimal(value)


class NullDecimalC(apgorm.Converter["Decimal | None", "int | None"]):
    def from_stored(self, value: Decimal | None) -> int | None:
        if value is None:
            return value
        return int(value)

    def to_stored(self, value: int | None) -> Decimal | None:
        if value is None:
            return value
        return Decimal(value)
