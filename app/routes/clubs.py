"""Club CRUD (docs/API.md, KAN-24).

GET    /api/clubs?university=   list, sorted by name
GET    /api/clubs/<id>          one club
POST   /api/clubs               create (201)
PATCH  /api/clubs/<id>          update the fields that are sent
DELETE /api/clubs/<id>          204, or 409 while the club still has events
"""
import re

from flask import Blueprint, jsonify, request
from sqlalchemy import func

from app.constants import UNIVERSITIES
from app.errors import ApiError
from app.extensions import db
from app.models import Club, Event

clubs_bp = Blueprint("clubs", __name__, url_prefix="/api/clubs")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
FIELDS = ("name", "university", "description", "contact_email", "logo_url")
FIX_FIELDS = "Please fix the highlighted fields."


def _body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ApiError(400, "Request body must be a JSON object.")
    return data


def _get_club(club_id):
    club = db.session.get(Club, club_id)
    if club is None:
        raise ApiError(404, "Club not found.")
    return club


def _validate(data, club=None):
    """Return (clean values, errors). For PATCH (club given), only sent fields are checked."""
    partial = club is not None
    clean, errors = {}, {}

    def sent(field):
        return field in data or not partial

    if sent("name"):
        name = data.get("name")
        if not isinstance(name, str) or not name.strip():
            errors["name"] = "Name is required."
        elif len(name.strip()) > 100:
            errors["name"] = "Name must be 100 characters or fewer."
        else:
            clean["name"] = name.strip()

    if sent("university"):
        university = data.get("university")
        if not isinstance(university, str) or not university.strip():
            errors["university"] = "University is required."
        elif university not in UNIVERSITIES:
            errors["university"] = "Choose a supported university."
        else:
            clean["university"] = university

    if sent("description"):
        description = data.get("description")
        if not isinstance(description, str) or not description.strip():
            errors["description"] = "Description is required."
        else:
            clean["description"] = description.strip()

    if "contact_email" in data:
        email = data["contact_email"]
        if email in (None, ""):
            clean["contact_email"] = None
        elif not isinstance(email, str) or not EMAIL_RE.match(email.strip()):
            errors["contact_email"] = "Enter a valid email address."
        else:
            clean["contact_email"] = email.strip()

    if "logo_url" in data:
        url = data["logo_url"]
        if url in (None, ""):
            clean["logo_url"] = None
        elif not isinstance(url, str) or not re.match(r"^https?://\S+$", url.strip()):
            errors["logo_url"] = "Enter a valid http(s) URL."
        else:
            clean["logo_url"] = url.strip()

    # Name must be unique within a university (checked on the final values)
    final_name = clean.get("name", club.name if club else None)
    final_university = clean.get("university", club.university if club else None)
    if "name" not in errors and "university" not in errors and final_name and final_university:
        query = Club.query.filter(
            func.lower(Club.name) == final_name.lower(),
            Club.university == final_university,
        )
        if club:
            query = query.filter(Club.id != club.id)
        if query.first():
            errors["name"] = "A club with this name already exists at this university."

    # An event's university must match its club's, so it can't change under events
    if (
        club
        and "university" in clean
        and clean["university"] != club.university
        and club.events
    ):
        errors["university"] = (
            "Move or delete this club's events before changing its university."
        )

    return clean, errors


@clubs_bp.get("")
def list_clubs():
    query = Club.query
    university = request.args.get("university")
    if university:
        query = query.filter(Club.university == university)
    clubs = query.order_by(func.lower(Club.name)).all()
    return jsonify([club.to_dict() for club in clubs])


@clubs_bp.get("/<int:club_id>")
def get_club(club_id):
    return jsonify(_get_club(club_id).to_dict())


@clubs_bp.post("")
def create_club():
    clean, errors = _validate(_body())
    if errors:
        raise ApiError(400, FIX_FIELDS, errors)

    club = Club(**{field: clean.get(field) for field in FIELDS})
    db.session.add(club)
    db.session.commit()
    return jsonify(club.to_dict()), 201


@clubs_bp.patch("/<int:club_id>")
def update_club(club_id):
    club = _get_club(club_id)
    clean, errors = _validate(_body(), club)
    if errors:
        raise ApiError(400, FIX_FIELDS, errors)

    for field, value in clean.items():
        setattr(club, field, value)
    db.session.commit()
    return jsonify(club.to_dict())


@clubs_bp.delete("/<int:club_id>")
def delete_club(club_id):
    club = _get_club(club_id)
    if db.session.query(Event.id).filter(Event.club_id == club.id).first():
        raise ApiError(409, "Club still has events.")

    db.session.delete(club)
    db.session.commit()
    return "", 204