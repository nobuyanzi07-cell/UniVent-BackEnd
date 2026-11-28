from app.errors import ApiError


def test_unknown_route_returns_an_error_string(client):
    res = client.get("/api/does-not-exist")
    assert res.status_code == 404
    assert isinstance(res.get_json()["error"], str)


def test_field_errors_use_the_errors_key(app, client):
    @app.get("/api/_validation")
    def _validation():
        raise ApiError(400, "Invalid.", {"name": "Name is required."})

    res = client.get("/api/_validation")
    assert res.status_code == 400
    assert res.get_json() == {"errors": {"name": "Name is required."}}


def test_conflict_uses_the_error_key(app, client):
    @app.get("/api/_conflict")
    def _conflict():
        raise ApiError(409, "Club still has events.")

    res = client.get("/api/_conflict")
    assert res.status_code == 409
    assert res.get_json() == {"error": "Club still has events."}


def test_unexpected_errors_return_500(app, client):
    @app.get("/api/_boom")
    def _boom():
        raise RuntimeError("boom")

    res = client.get("/api/_boom")
    assert res.status_code == 500
    assert res.get_json() == {"error": "Internal server error."}