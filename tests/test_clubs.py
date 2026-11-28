from datetime import datetime

from app.constants import UNIVERSITIES
from app.extensions import db
from app.models import Club, Event

UNI_A, UNI_B = UNIVERSITIES[0], UNIVERSITIES[1]


def club_payload(**overrides):
    payload = {
        "name": "Tech Society",
        "university": UNI_A,
        "description": "Workshops and hackathons.",
        "contact_email": "tech@example.com",
        "logo_url": None,
    }
    payload.update(overrides)
    return payload


def make_club(client, **overrides):
    res = client.post("/api/clubs", json=club_payload(**overrides))
    assert res.status_code == 201, res.get_json()
    return res.get_json()


def add_event(club_id):
    club = db.session.get(Club, club_id)
    event = Event(
        title="Hack Night",
        category="Technology",
        description="Build something.",
        start_at=datetime(2030, 1, 1, 18, 0),
        venue="Main Hall",
        city="Nairobi",
        university_id=club.university_id,
        club_id=club_id,
    )
    db.session.add(event)
    db.session.commit()
    return event


def fields_of(res):
    return res.get_json()["error"]["fields"]


# --- list ---------------------------------------------------------------


def test_list_is_empty_at_first(client):
    res = client.get("/api/clubs")
    assert res.status_code == 200
    assert res.get_json() == []


def test_list_is_sorted_by_name(client):
    make_club(client, name="Zebra Club")
    make_club(client, name="alpha Club")
    make_club(client, name="Music Society")

    names = [c["name"] for c in client.get("/api/clubs").get_json()]
    assert names == ["alpha Club", "Music Society", "Zebra Club"]


def test_list_filters_by_university(client):
    make_club(client, name="A Club", university=UNI_A)
    make_club(client, name="B Club", university=UNI_B)

    res = client.get("/api/clubs", query_string={"university": UNI_B})
    assert [c["name"] for c in res.get_json()] == ["B Club"]


# --- detail -------------------------------------------------------------


def test_get_returns_the_club(client):
    created = make_club(client)
    res = client.get(f"/api/clubs/{created['id']}")
    assert res.status_code == 200
    assert res.get_json() == {**created, "events": []}


def test_get_missing_club_is_404(client):
    res = client.get("/api/clubs/999")
    assert res.status_code == 404
    assert res.get_json()["error"] == {"status": 404, "message": "Club not found."}


# --- create -------------------------------------------------------------


def test_create_returns_201_with_the_club(client):
    res = client.post("/api/clubs", json=club_payload())
    assert res.status_code == 201
    body = res.get_json()
    assert body["id"] > 0
    assert body["name"] == "Tech Society"
    assert body["university"] == UNI_A
    assert body["contact_email"] == "tech@example.com"
    assert body["logo_url"] is None
    assert body["created_at"].endswith("Z")


def test_create_without_required_fields_is_400(client):
    res = client.post("/api/clubs", json={})
    assert res.status_code == 400
    assert set(fields_of(res)) == {"name", "university", "description"}
    assert fields_of(res)["name"] == "Name is required."


def test_create_rejects_a_body_that_is_not_an_object(client):
    res = client.post("/api/clubs", json=["nope"])
    assert res.status_code == 400
    assert res.get_json()["error"]["message"] == "Request body must be a JSON object."


def test_create_validates_each_field(client):
    res = client.post(
        "/api/clubs",
        json=club_payload(
            name="x" * 101,
            university="Not A University",
            contact_email="not-an-email",
            logo_url="ftp://nope",
        ),
    )
    assert res.status_code == 400
    assert set(fields_of(res)) == {"name", "university", "contact_email", "logo_url"}
    assert fields_of(res)["contact_email"] == "Enter a valid email address."


def test_create_accepts_missing_optional_fields(client):
    res = client.post(
        "/api/clubs",
        json={"name": "Bare", "university": UNI_A, "description": "Just a club."},
    )
    assert res.status_code == 201
    assert res.get_json()["contact_email"] is None


def test_club_names_are_unique_within_a_university(client):
    make_club(client, name="Tech Society", university=UNI_A)

    dupe = client.post("/api/clubs", json=club_payload(name="tech society", university=UNI_A))
    assert dupe.status_code == 400
    assert "name" in fields_of(dupe)

    other = client.post("/api/clubs", json=club_payload(name="Tech Society", university=UNI_B))
    assert other.status_code == 201


# --- update -------------------------------------------------------------


def test_patch_updates_only_the_sent_fields(client):
    created = make_club(client)
    res = client.patch(f"/api/clubs/{created['id']}", json={"description": "New text."})
    assert res.status_code == 200
    body = res.get_json()
    assert body["description"] == "New text."
    assert body["name"] == created["name"]
    assert body["contact_email"] == created["contact_email"]


def test_patch_can_clear_optional_fields(client):
    created = make_club(client)
    res = client.patch(f"/api/clubs/{created['id']}", json={"contact_email": None})
    assert res.status_code == 200
    assert res.get_json()["contact_email"] is None


def test_patch_validates_like_post(client):
    created = make_club(client)
    res = client.patch(f"/api/clubs/{created['id']}", json={"name": "", "contact_email": "bad"})
    assert res.status_code == 400
    assert set(fields_of(res)) == {"name", "contact_email"}


def test_patch_cannot_rename_onto_an_existing_club(client):
    make_club(client, name="First")
    second = make_club(client, name="Second")
    res = client.patch(f"/api/clubs/{second['id']}", json={"name": "First"})
    assert res.status_code == 400
    assert "name" in fields_of(res)


def test_patch_keeping_the_same_name_is_fine(client):
    created = make_club(client)
    res = client.patch(f"/api/clubs/{created['id']}", json={"name": created["name"]})
    assert res.status_code == 200


def test_patch_missing_club_is_404(client):
    res = client.patch("/api/clubs/999", json={"name": "Ghost"})
    assert res.status_code == 404


def test_patch_cannot_change_university_while_the_club_has_events(client, app):
    created = make_club(client)
    add_event(created["id"])

    res = client.patch(f"/api/clubs/{created['id']}", json={"university": UNI_B})
    assert res.status_code == 400
    assert "university" in fields_of(res)


def test_patch_can_change_university_without_events(client):
    created = make_club(client)
    res = client.patch(f"/api/clubs/{created['id']}", json={"university": UNI_B})
    assert res.status_code == 200
    assert res.get_json()["university"] == UNI_B


# --- delete -------------------------------------------------------------


def test_delete_returns_204_and_removes_the_club(client):
    created = make_club(client)
    res = client.delete(f"/api/clubs/{created['id']}")
    assert res.status_code == 204
    assert res.data == b""
    assert client.get(f"/api/clubs/{created['id']}").status_code == 404


def test_delete_missing_club_is_404(client):
    assert client.delete("/api/clubs/999").status_code == 404


def test_delete_is_blocked_while_the_club_has_events(client, app):
    created = make_club(client)
    add_event(created["id"])

    res = client.delete(f"/api/clubs/{created['id']}")
    assert res.status_code == 409
    assert res.get_json()["error"]["message"] == "Club still has events."
    assert db.session.get(Club, created["id"]) is not None



def test_get_club_includes_its_events(client, app):
    created = make_club(client)
    add_event(created["id"])

    res = client.get(f"/api/clubs/{created['id']}")

    assert res.status_code == 200
    events = res.get_json()["events"]
    assert len(events) == 1
    assert events[0]["title"] == "Hack Night"