"""Identity abstraction (contract D5).

DEV uses a simple ``X-User-Ref`` header (default ``dev-user``). The whole
app sees only :class:`Actor` — replacing this ``get_actor`` with a
corporate-IdP/JWT implementation later must not touch any Product record
or calling endpoint code. Audit stores the opaque ``user_ref`` string.
"""

from dataclasses import dataclass

from fastapi import Request

DEFAULT_DEV_USER = "dev-user"


@dataclass(frozen=True)
class Actor:
    user_ref: str


def get_actor(request: Request) -> Actor:
    """DEV actor resolution: trusted ``X-User-Ref`` header.

    Production replacement point: parse/validate an IdP token here and
    map it to the same ``Actor(user_ref)`` model.
    """
    ref = request.headers.get("X-User-Ref") or DEFAULT_DEV_USER
    return Actor(user_ref=ref.strip())
