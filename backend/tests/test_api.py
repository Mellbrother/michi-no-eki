from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "ok"
    assert "timestamp" in body


def test_list_stations_and_detail():
    response = client.get("/stations")
    assert response.status_code == 200
    stations = response.json()
    assert len(stations) >= 2

    station_id = stations[0]["id"]
    detail = client.get(f"/stations/{station_id}")
    assert detail.status_code == 200
    assert detail.json()["id"] == station_id


def test_prefecture_stats():
    response = client.get("/prefectures")
    assert response.status_code == 200
    body = response.json()
    assert body[0]["prefecture"]

    catalog = client.get("/prefectures/北海道/stations")
    assert catalog.status_code == 200
    assert all(station["prefecture"] == "北海道" for station in catalog.json())


def test_profile_and_progress():
    me = client.get("/users/me")
    assert me.status_code == 200
    profile = me.json()
    assert profile["display_name"]

    progress = client.get("/progress/overall")
    assert progress.status_code == 200
    body = progress.json()
    assert body["total_stations"] >= body["stamped"]


def test_auth_and_stamps_flow():
    login = client.post("/auth/login", params={"email": "taro@example.com", "password": "secret"})
    assert login.status_code == 200
    assert login.json()["access_token"]

    stamp_payload = {"station_id": 1, "source": "gps"}
    created = client.post("/stamps", json=stamp_payload)
    assert created.status_code == 200
    stamp_body = created.json()
    assert stamp_body["points_awarded"] == 10
    assert stamp_body["stamp"]["station_id"] == 1

    history = client.get("/users/me/stamps", params={"station_id": 1})
    assert history.status_code == 200
    assert any(item["station_id"] == 1 for item in history.json())


def test_achievements_listing():
    response = client.get("/achievements")
    assert response.status_code == 200
    achievements = response.json()
    assert any(ach["code"] == "first_stamp" for ach in achievements)


def test_patch_user_profile():
    payload = {
        "id": 1,
        "display_name": "旅人花子",
        "email": "hanako@example.com",
        "total_points": 200,
        "total_stamps": 10,
        "prefecture_completion_rate": 0.5,
    }
    response = client.patch("/users/me", json=payload)
    assert response.status_code == 200
    updated = response.json()
    assert updated["display_name"] == "旅人花子"
    assert updated["total_points"] == 200
    assert updated["prefecture_completion_rate"] == 0.5


def test_user_achievements_endpoint_returns_filtered():
    response = client.get("/users/1/achievements")
    assert response.status_code == 200
    assert all(item["code"] for item in response.json())

    empty = client.get("/users/999/achievements")
    assert empty.status_code == 200
    assert empty.json() == []
