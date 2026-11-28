from datetime import datetime, timezone

from .extensions import db


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _stamp(value):
    return value.strftime("%Y-%m-%dT%H:%M:%SZ") if value else None


class University(db.Model):
    __tablename__ = "universities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    short_name = db.Column(db.String(20), nullable=False)

    clubs = db.relationship("Club", back_populates="university")
    events = db.relationship("Event", back_populates="university")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "short_name": self.short_name}


class Club(db.Model):
    __tablename__ = "clubs"
    __table_args__ = (
        db.UniqueConstraint("name", "university_id", name="uq_club_name_university"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    university_id = db.Column(
        db.Integer, db.ForeignKey("universities.id"), nullable=False, index=True
    )
    description = db.Column(db.Text, nullable=False)
    contact_email = db.Column(db.String(255))
    logo_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, nullable=False, default=_utcnow)

    university = db.relationship("University", back_populates="clubs")
    events = db.relationship("Event", back_populates="club", order_by="Event.start_at")

    def to_dict(self, include_events=False):
        data = {
            "id": self.id,
            "name": self.name,
            "university": self.university.name,
            "university_id": self.university_id,
            "description": self.description,
            "contact_email": self.contact_email,
            "logo_url": self.logo_url,
            "created_at": _stamp(self.created_at),
        }
        if include_events:
            data["events"] = [event.to_dict(include_club=False) for event in self.events]
        return data


class Event(db.Model):
    __tablename__ = "events"
    __table_args__ = (
        db.CheckConstraint("price_kes >= 0", name="ck_event_price_non_negative"),
        db.CheckConstraint(
            "capacity IS NULL OR capacity >= 0", name="ck_event_capacity_non_negative"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), index=True)
    start_at = db.Column(db.DateTime, nullable=False, index=True)
    venue = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100))
    image_url = db.Column(db.String(500))
    price_kes = db.Column(db.Integer, nullable=False, default=0)
    capacity = db.Column(db.Integer)
    club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"), nullable=False, index=True)
    university_id = db.Column(
        db.Integer, db.ForeignKey("universities.id"), nullable=False, index=True
    )
    created_at = db.Column(db.DateTime, nullable=False, default=_utcnow)

    club = db.relationship("Club", back_populates="events")
    university = db.relationship("University", back_populates="events")
    saved_entries = db.relationship(
        "SavedEvent", back_populates="event", cascade="all, delete-orphan"
    )

    def to_dict(self, include_club=True):
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "start_at": _stamp(self.start_at),
            "venue": self.venue,
            "city": self.city,
            "image_url": self.image_url,
            "price_kes": self.price_kes,
            "capacity": self.capacity,
            "club_id": self.club_id,
            "university_id": self.university_id,
            "created_at": _stamp(self.created_at),
        }
        if include_club:
            data["club"] = {
                "id": self.club.id,
                "name": self.club.name,
                "logo_url": self.club.logo_url,
            }
            data["university"] = self.university.to_dict()
        return data


class SavedEvent(db.Model):
    __tablename__ = "saved_events"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(
        db.Integer, db.ForeignKey("events.id"), nullable=False, unique=True
    )
    created_at = db.Column(db.DateTime, nullable=False, default=_utcnow)

    event = db.relationship("Event", back_populates="saved_entries")

    def to_dict(self):
        return {
            "id": self.id,
            "event_id": self.event_id,
            "created_at": _stamp(self.created_at),
            "event": self.event.to_dict(),
        }