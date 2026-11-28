"""GET /api/universities: seeded reference data for filters and form dropdowns (FR-12)."""
from flask import Blueprint, jsonify

from app.models import University

universities_bp = Blueprint("universities", __name__, url_prefix="/api/universities")


@universities_bp.get("")
def list_universities():
    universities = University.query.order_by(University.name).all()
    return jsonify([university.to_dict() for university in universities])
