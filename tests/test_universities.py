from app.constants import UNIVERSITIES


def test_list_universities_returns_all_seeded(client):
    res = client.get("/api/universities")

    assert res.status_code == 200
    body = res.get_json()
    assert [u["name"] for u in body] == sorted(UNIVERSITIES)


def test_university_has_id_name_and_short_name(client):
    res = client.get("/api/universities")

    first = res.get_json()[0]
    assert set(first) == {"id", "name", "short_name"}
    