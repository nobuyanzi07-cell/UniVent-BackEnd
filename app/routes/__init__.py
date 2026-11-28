"""Blueprints. Teammates add theirs here (events, clubs, saved, universities)."""
from .clubs import clubs_bp
from .featured import featured_bp
from .health import health_bp

ALL_BLUEPRINTS = [health_bp, featured_bp, clubs_bp]