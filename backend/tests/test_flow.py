"""End-to-end happy path: register -> draft -> generate -> publish -> read."""


async def test_full_authoring_flow(client):
    # Register and get a token
    res = await client.post(
        "/api/auth/register",
        json={
            "email": "author@example.com",
            "display_name": "Author",
            "password": "supersecret",
        },
    )
    assert res.status_code == 201
    token = res.json()["access_token"]
    auth = {"Authorization": f"Bearer {token}"}

    # Create a draft brief
    res = await client.post(
        "/api/drafts",
        headers=auth,
        json={"topic": "Async Python", "tone": "technical"},
    )
    assert res.status_code == 201
    draft_id = res.json()["id"]
    assert res.json()["status"] == "pending"

    # Generate content (uses the fake writer)
    res = await client.post(f"/api/drafts/{draft_id}/generate", headers=auth)
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ready"
    assert body["reading_time_minutes"] == 5
    assert body["title"] == "On Async Python"

    # Publish
    res = await client.post(f"/api/drafts/{draft_id}/publish", headers=auth)
    assert res.status_code == 201
    slug = res.json()["slug"]

    # Read publicly (no auth)
    res = await client.get(f"/api/posts/{slug}")
    assert res.status_code == 200
    assert res.json()["title"] == "On Async Python"

    res = await client.get("/api/posts")
    assert res.status_code == 200
    assert len(res.json()) == 1


async def test_requires_auth(client):
    res = await client.get("/api/drafts")
    assert res.status_code == 401
