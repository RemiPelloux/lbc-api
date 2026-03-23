from __future__ import annotations

from enum import Enum
from typing import TypeVar, overload

E = TypeVar("E", bound=Enum)


@overload
def parse_enum_member(enum_cls: type[E], raw: str | None, default: E) -> E: ...


@overload
def parse_enum_member(enum_cls: type[E], raw: str | None, default: None) -> E | None: ...


def parse_enum_member(enum_cls: type[E], raw: str | None, default: E | None) -> E | None:
    if raw is None:
        return default
    try:
        return enum_cls[raw]
    except KeyError:
        for member in enum_cls:
            if member.name == raw or str(member.value) == raw:
                return member
    raise ValueError(f"Unknown value {raw!r} for {enum_cls.__name__}")
