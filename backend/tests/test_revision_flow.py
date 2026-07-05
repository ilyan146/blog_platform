"""The 'revise my own draft' flow: stream progress + a result, then save it
as an editable, publishable Draft — using the fake researcher/writer from
conftest (no Azure, no Playwright subprocess).
"""

import json


async def _register(client) -> dict:
    res = await client.post(
        "/api/auth/register",
        json={
            "email": "reviser@example.com",
            "display_name": "Reviser",
            "password": "supersecret",
        },
    )
    assert res.status_code == 201
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


async def test_stream_revision_yields_a_done_event(client):
    auth = await _register(client)

    async with client.stream(
        "POST",
        "/api/revisions/stream",
        headers=auth,
        json={"draft_text": "My own draft. See https://example.com/source for more."},
    ) as res:
        assert res.status_code == 200
        events = []
        async for line in res.aiter_lines():
            if line.startswith("data: "):
                events.append(json.loads(line[len("data: ") :]))

    assert events, "expected at least one SSE event"
    done = events[-1]
    assert done["type"] == "done"
    assert done["title"] == "Revised draft"
    assert done["reading_time_minutes"] == 5


async def test_save_revision_as_draft_is_editable_and_publishable(client):
    auth = await _register(client)

    res = await client.post(
        "/api/drafts/from-revision",
        headers=auth,
        json={
            "title": "My Revised Post",
            "excerpt": "A concise, deterministic excerpt for testing purposes.",
            "body_markdown": " ".join(["word"] * 1100),
            "tags": ["revised"],
        },
    )
    assert res.status_code == 201
    draft = res.json()
    assert draft["status"] == "ready"
    draft_id = draft["id"]

    # Editable via the existing edit endpoint.
    res = await client.put(
        f"/api/drafts/{draft_id}",
        headers=auth,
        json={
            "title": "My Revised Post (edited)",
            "excerpt": "A concise, deterministic excerpt for testing purposes.",
            "body_markdown": " ".join(["word"] * 1100),
            "tags": ["revised"],
        },
    )
    assert res.status_code == 200
    assert res.json()["title"] == "My Revised Post (edited)"

    # Publishable via the existing publish endpoint.
    res = await client.post(f"/api/drafts/{draft_id}/publish", headers=auth)
    assert res.status_code == 201
    assert res.json()["title"] == "My Revised Post (edited)"
