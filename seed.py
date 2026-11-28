from datetime import datetime

from app import create_app
from app.constants import UNIVERSITIES
from app.extensions import db
from app.models import Club, Event, University
SHORT_NAMES = {
    "University of Nairobi": "UoN",
    "Strathmore University": "SU",
    "Kenyatta University": "KU",
    "Jomo Kenyatta University of Agriculture and Technology": "JKUAT",
    "Technical University of Kenya": "TUK",
}


def seed_universities():
    for name in UNIVERSITIES:
        if not University.query.filter_by(name=name).first():
            db.session.add(University(name=name, short_name=SHORT_NAMES[name]))
    db.session.commit()

CLUBS = [
    {"university": "University of Nairobi", "name": "UoN Drama Club", "description": "Theatre, skits and stage productions.", "contact_email": "drama@uon.example"},
    {"university": "University of Nairobi", "name": "UoN Photography Society", "description": "Photo walks, exhibitions and editing workshops.", "contact_email": "photo@uon.example"},
    {"university": "Strathmore University", "name": "Strathmore Entrepreneurship Club", "description": "Startup pitches and business mentorship.", "contact_email": "ent@su.example"},
    {"university": "Strathmore University", "name": "Strathmore Debate Society", "description": "Weekly debates and inter-university tournaments.", "contact_email": "debate@su.example"},
    {"university": "Kenyatta University", "name": "KU Tech Club", "description": "Coding, hackathons and tech talks.", "contact_email": "tech@ku.example"},
    {"university": "Kenyatta University", "name": "KU Choir", "description": "Choral music and campus concerts.", "contact_email": "choir@ku.example"},
    {"university": "Jomo Kenyatta University of Agriculture and Technology", "name": "JKUAT Robotics Club", "description": "Building robots and competing in engineering challenges.", "contact_email": "robotics@jkuat.example"},
    {"university": "Jomo Kenyatta University of Agriculture and Technology", "name": "JKUAT Hiking Club", "description": "Weekend hikes and outdoor trips.", "contact_email": "hiking@jkuat.example"},
    {"university": "Technical University of Kenya", "name": "TUK Music Society", "description": "Live music nights and open mics.", "contact_email": "music@tuk.example"},
    {"university": "Technical University of Kenya", "name": "TUK Innovation Hub", "description": "Prototyping, design sprints and demo days.", "contact_email": "innovation@tuk.example"},
]


def seed_clubs():
    for data in CLUBS:
        university = University.query.filter_by(name=data["university"]).first()
        exists = Club.query.filter_by(
            university_id=university.id, name=data["name"]
        ).first()
        if not exists:
            db.session.add(
                Club(
                    name=data["name"],
                    description=data["description"],
                    contact_email=data["contact_email"],
                    university_id=university.id,
                )
            )
    db.session.commit()

EVENTS = [
    {"club": "UoN Drama Club", "title": "Campus Theatre Night", "category": "Arts", "description": "An evening of short plays written and performed by students.", "start_at": datetime(2026, 12, 5, 18, 0), "venue": "Taifa Hall", "price_kes": 200, "capacity": 300},
    {"club": "UoN Photography Society", "title": "Photo Walk: Nairobi CBD", "category": "Arts", "description": "A guided photo walk through the city centre, with tips from senior members.", "start_at": datetime(2026, 12, 6, 9, 0), "venue": "Main Gate, Chiromo Campus", "price_kes": 0, "capacity": 40},
    {"club": "Strathmore Entrepreneurship Club", "title": "Startup Pitch Day", "category": "Business", "description": "Student founders pitch to a panel of mentors and investors.", "start_at": datetime(2026, 12, 10, 14, 0), "venue": "Strathmore Business School", "price_kes": 500, "capacity": 120},
    {"club": "Strathmore Debate Society", "title": "Inter-University Debate Final", "category": "Social", "description": "The final round of this year's inter-university debate tournament.", "start_at": datetime(2026, 12, 11, 15, 0), "venue": "Strathmore Auditorium", "price_kes": 0, "capacity": 250},
    {"club": "KU Tech Club", "title": "KU Hackathon 2026", "category": "Tech", "description": "A 24-hour hackathon to build a solution for a campus problem.", "start_at": datetime(2026, 12, 8, 9, 0), "venue": "KU Main Auditorium", "price_kes": 0, "capacity": 150},
    {"club": "KU Choir", "title": "Christmas Carols Concert", "category": "Music", "description": "The KU Choir performs a programme of carols and gospel favourites.", "start_at": datetime(2026, 12, 12, 17, 0), "venue": "KU Chapel", "price_kes": 100, "capacity": 400},
    {"club": "JKUAT Robotics Club", "title": "Robotics Showdown", "category": "Tech", "description": "Teams compete with robots they built to complete an obstacle course.", "start_at": datetime(2026, 12, 15, 10, 0), "venue": "JKUAT Engineering Workshop", "price_kes": 100, "capacity": 100},
    {"club": "JKUAT Hiking Club", "title": "Ngong Hills Sunrise Hike", "category": "Sports", "description": "An early-morning group hike with breakfast at the summit.", "start_at": datetime(2026, 12, 19, 5, 30), "venue": "Ngong Hills Gate", "price_kes": 800, "capacity": 60},
    {"club": "TUK Music Society", "title": "Open Mic Night", "category": "Music", "description": "Sing, rap or play an instrument. All performers are welcome.", "start_at": datetime(2026, 12, 12, 19, 0), "venue": "TUK Amphitheatre", "price_kes": 0, "capacity": 200},
    {"club": "TUK Innovation Hub", "title": "Demo Day", "category": "Tech", "description": "Student teams demo prototypes they built over a semester.", "start_at": datetime(2027, 1, 22, 13, 0), "venue": "TUK Innovation Hub", "price_kes": 0, "capacity": 80},
]


def seed_events():
    for data in EVENTS:
        club = Club.query.filter_by(name=data["club"]).first()
        exists = Event.query.filter_by(club_id=club.id, title=data["title"]).first()
        if not exists:
            db.session.add(
                Event(
                    title=data["title"],
                    category=data["category"],
                    description=data["description"],
                    start_at=data["start_at"],
                    venue=data["venue"],
                    city="Nairobi",
                    price_kes=data["price_kes"],
                    capacity=data["capacity"],
                    club_id=club.id,
                    university_id=club.university_id,
                )
            )
    db.session.commit()


def run_seed():
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_universities()
        seed_clubs()
        seed_events()
        print("Seed complete.")


if __name__ == "__main__":
    run_seed()
    

