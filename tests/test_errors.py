from app.errors import ApiError


def test_unknown_route_uses_the_error_shape(client):
    res = client.get("/api/does-not-exist")
    assert res.status_code == 404
    error = res.get_json()["error"]
    assert error["status"] == 404
    assert isinstance(error["message"], str)
    assert "fields" not in error


def test_wrong_method_returns_405(client):
    res = client.post("/api/health")
    assert res.status_code == 405
    assert res.get_json()["error"]["status"] == 405


def test_api_error_includes_fields(app, client):
    @app.get("/api/_validation")
    def _validation():
        raise ApiError(400, "Please fix the highlighted fields.", {"name": "Name is required."})

    res = client.get("/api/_validation")
    assert res.status_code == 400
    assert res.get_json() == {
        "error": {
            "status": 400,
            "message": "Please fix the highlighted fields.",
            "fields": {"name": "Name is required."},
        }
    }


def test_api_error_without_fields_omits_the_key(app, client):
    @app.get("/api/_conflict")
    def _conflict():
        raise ApiError(409, "Club still has events.")

    res = client.get("/api/_conflict")
    assert res.status_code == 409
    assert res.get_json() == {
        "error": {"status": 409, "message": "Club still has events."}
    }


def test_unexpected_errors_return_500(app, client):
    @app.get("/api/_boom")
    def _boom():
        raise RuntimeError("boom")

    res = client.get("/api/_boom")
    assert res.status_code == 500
    assert res.get_json()["error"]["status"] == 500