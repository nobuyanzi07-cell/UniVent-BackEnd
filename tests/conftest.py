import pytest

from app import create_app
from app.constants import UNIVERSITIES
from app.extensions import db
from app.models import University


@pytest.fixture()
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        # Clubs and events need a University row, so every test starts with them
        for name in UNIVERSITIES:
            db.session.add(University(name=name, short_name=name[:20]))
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
    