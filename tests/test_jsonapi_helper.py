"""Tests for the JSON:API serialization helpers."""

from __future__ import annotations

from pulse_sandbox.productive.jsonapi import envelope, make_resource, to_many_rel, to_one_rel


def test_make_resource_minimal() -> None:
    res = make_resource("people", "701")
    assert res == {"type": "people", "id": "701", "attributes": {}}


def test_make_resource_with_attributes_and_relationships() -> None:
    res = make_resource(
        "projects",
        "801",
        attributes={"name": "Acme"},
        relationships={"company": {"data": {"type": "companies", "id": "501"}}},
    )
    assert res["type"] == "projects"
    assert res["id"] == "801"
    assert res["attributes"]["name"] == "Acme"
    assert res["relationships"]["company"]["data"]["id"] == "501"


def test_make_resource_coerces_int_id_to_str() -> None:
    res = make_resource("people", 701)
    assert res["id"] == "701"


def test_to_one_rel() -> None:
    rel = to_one_rel("companies", "501")
    assert rel == {"data": {"type": "companies", "id": "501"}}


def test_to_one_rel_with_none() -> None:
    rel = to_one_rel("companies", None)
    assert rel == {"data": None}


def test_to_many_rel() -> None:
    rel = to_many_rel("teams", ["401", "402"])
    assert rel["data"] == [
        {"type": "teams", "id": "401"},
        {"type": "teams", "id": "402"},
    ]


def test_to_many_rel_coerces_int_ids() -> None:
    rel = to_many_rel("teams", [401, 402])
    assert all(item["id"] == str(i) for item, i in zip(rel["data"], [401, 402]))


def test_envelope_explicit_null_next_link() -> None:
    """Pulse's pagination loop checks `links.next` — must be null when no more pages."""
    body = envelope([{"id": "1", "type": "x", "attributes": {}}])
    assert body["data"][0]["id"] == "1"
    assert body["links"]["next"] is None


def test_envelope_with_included_and_next() -> None:
    body = envelope(
        data=[{"id": "1", "type": "x", "attributes": {}}],
        included=[{"id": "2", "type": "y", "attributes": {}}],
        next_link="/page/2",
    )
    assert body["included"][0]["id"] == "2"
    assert body["links"]["next"] == "/page/2"


def test_envelope_omits_included_when_empty() -> None:
    body = envelope(data=[])
    assert "included" not in body or body.get("included") in ([], None)
