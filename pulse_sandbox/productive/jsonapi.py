"""Minimal JSON:API serialization helpers tuned for Productive's response shape."""

from __future__ import annotations

from typing import Any


def make_resource(
    type_: str,
    id_: str,
    attributes: dict[str, Any] | None = None,
    relationships: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a single JSON:API resource object."""
    res: dict[str, Any] = {
        "type": type_,
        "id": str(id_),
        "attributes": attributes or {},
    }
    if relationships:
        res["relationships"] = relationships
    return res


def to_one_rel(type_: str, id_: str | int | None) -> dict[str, Any]:
    """Build a to-one relationship link object."""
    if id_ is None:
        return {"data": None}
    return {"data": {"type": type_, "id": str(id_)}}


def to_many_rel(type_: str, ids: list[str | int]) -> dict[str, Any]:
    """Build a to-many relationship link object."""
    return {"data": [{"type": type_, "id": str(i)} for i in ids]}


def envelope(
    data: list[dict[str, Any]] | dict[str, Any],
    included: list[dict[str, Any]] | None = None,
    next_link: str | None = None,
) -> dict[str, Any]:
    """Wrap a JSON:API response with optional `included` and `links.next`."""
    body: dict[str, Any] = {"data": data}
    if included:
        body["included"] = included
    body["links"] = {"next": next_link}  # explicit null if no next page — Pulse checks this
    return body
