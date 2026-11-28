from datetime import datetime, timezone

from .extensions import db


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Club(db.Model):
    __tablename__ = "clubs"
    __table_args__ = (
        db.UniqueConstraint("name", "university", name="uq_club_name_university"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    university = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    contact_email = db.Column(db.String(255))
    logo_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, nullable=False, default=_utcnow)

    events = db.relationship("Event", back_populates="club")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "university": self.university,
            "description": self.description,
            "contact_email": self.contact_email,
            "logo_url": self.logo_url,
            "created_at": self.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time)
    venue = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False, default=0)
    image_url = db.Column(db.String(500))
    university = db.Column(db.String(150), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=_utcnow)

    club = db.relationship("Club", back_populates="events")