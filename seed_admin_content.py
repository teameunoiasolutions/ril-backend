"""Seed an admin account and the initial site content (themes, places, packages).

Run once (after a working DATABASE_URL) with:

    python seed_admin_content.py

Admin login created:
    email:    admin@royaleisles.lk
    password: admin12345
"""

from app.database.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import Admin, Package, Place, Theme

ADMIN_EMAIL = "admin@royaleisles.lk"
ADMIN_PASSWORD = "admin12345"

THEMES = [
    ("Wildlife & Wilderness", "Leopards, elephants, forests, field researchers, remote ecosystems, and nature without performance.", "For the Seeker of Silence", "The Leopard Research Circuit"),
    ("Ocean & Discovery", "Whale paths, quiet lagoons, sailing days, and coastlines that reveal themselves with patience.", "For the Unhurried Wanderer", "The Deep-Water Hour"),
    ("Heritage & Memory", "Ancient kingdoms, sacred spaces, archaeology, historians, and living traditions carried forward.", "For the Heritage Guardian", "The Sigiriya Dawn Ascent"),
    ("Wellness & Restoration", "Ayurveda, healing traditions, retreats, slow living, and the quiet work of personal renewal.", "For the Restorer", "The Ancient Grammar of Healing"),
    ("Rail & Landscape", "Hill country train journeys, tea estates, mountain routes, and scenery that changes by the hour.", "For the Reflective Wanderer", "A Private Tea Estate, Locked Before Dawn"),
    ("Culture & Human Connection", "Artisans, musicians, dancers, family traditions, private introductions, and everyday Sri Lanka.", "For the Curious Witness", "A Private Kandyan Dance Rehearsal"),
    ("Shared Heritage", "Rolling tea estates, timeless hill stations, railway journeys, old gardens, and civic architecture reveal a chapter of Sri Lanka's story still visible in daily life.", "For the Thoughtful Historian", "Shared Heritage, Quietly Read"),
]

# A representative starter set of places (name, region, description, lng, lat, best_time, activities).
PLACES_BY_THEME = {
    "Wildlife & Wilderness": [
        ("Yala", "Southern Province", "Sri Lanka's most celebrated leopard country and dry-zone wilderness.", 81.5216, 6.3728, "February - September", ["Private safaris", "Naturalist mornings"]),
    ],
    "Ocean & Discovery": [
        ("Mirissa", "Southern Coast", "A crescent bay known for blue-whale mornings and quiet sailing days.", 80.4718, 5.9483, "December - April", ["Whale watching", "Private sailing"]),
        ("Tangalle", "Southern Coast", "Untouched southern bays and slow, private beach time.", 80.7911, 6.024, "November - April", ["Hidden beaches", "Coastal walks"]),
    ],
    "Heritage & Memory": [
        ("Sigiriya", "Cultural Triangle", "The 5th-century rock fortress rising above the central plains.", 80.7603, 7.9570, "May - October", ["Dawn ascent", "Fresco viewing"]),
        ("Anuradhapura", "Cultural Triangle", "The island's first great capital and sacred monastic city.", 80.4037, 8.3114, "May - October", ["Sacred Bodhi Tree", "Dagoba tour"]),
    ],
    "Rail & Landscape": [
        ("Nuwara Eliya", "Hill Country", "Cool, misted tea country and colonial-era hill-station calm.", 80.7829, 6.9497, "Year-round", ["Estate lunches", "Tea tastings"]),
        ("Ella", "Uva Highlands", "Mountain walks, the Nine Arches Bridge, and highland rail.", 81.0462, 6.8667, "January - March", ["Nine Arches walk", "Highland rail"]),
    ],
    "Culture & Human Connection": [
        ("Kandy", "Central Highlands", "A sacred hill capital of temple bells and living Kandyan culture.", 80.6350, 7.2906, "Year-round", ["Temple rituals", "Private guiding"]),
    ],
}

PACKAGES = [
    {
        "name": "Discovery", "numeral": "I", "duration": "10 Days",
        "character": "Brisk and spirited. The island's defining sights gathered without a wasted morning.",
        "route": ["Colombo", "Sigiriya (Cultural Triangle)", "Kandy", "Nuwara Eliya", "Yala National Park", "Galle", "Airport"],
        "inclusions": ["The Sigiriya rock ascent", "The Temple of the Tooth", "A scenic hill-country rail journey", "A private wildlife safari", "A walking tour of historic Galle Fort"],
        "pace": "Brisk", "best_for": "First visits and shorter diaries", "reach": "West, Centre & South", "price_from": 4850, "sort_order": 0,
    },
    {
        "name": "Deep Dive", "numeral": "II", "duration": "16 Days",
        "character": "Immersive and unhurried. The celebrated landmarks with the time to sit with them.",
        "route": ["Negombo", "Anuradhapura", "Trincomalee (East Coast)", "Sigiriya", "Kandy", "Ella", "Udawalawe National Park", "Mirissa Beach", "Galle", "Airport"],
        "inclusions": ["The UNESCO ancient cities", "Whale watching or quiet beach days at Trincomalee", "Mountain walking above Ella", "A visit to the elephant transit home", "Surfing lessons on the southern coast"],
        "pace": "Measured", "best_for": "Travellers who prefer depth to distance", "reach": "North-Central, East, Hills & South", "price_from": 7900, "sort_order": 1,
    },
    {
        "name": "Dynasty", "numeral": "III", "duration": "21 Days",
        "character": "The grand overland passage. The entire island read from north to south.",
        "route": ["Colombo", "Wilpattu National Park", "Jaffna (The Far North)", "Trincomalee", "Cultural Triangle", "Kandy", "Knuckles Range", "Nuwara Eliya & Ella", "Yala", "Tangalle & Hiriketiya", "Galle", "Airport"],
        "inclusions": ["Remote northern culture and island-hopping around Jaffna", "Leopard safaris in Wilpattu", "Trekking in the Knuckles mountain range", "Slow, unhurried days along the untouched southern bays"],
        "pace": "Unhurried", "best_for": "Returning travellers and grand tours", "reach": "The entire island, north to south", "price_from": 12400, "sort_order": 2,
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Admin (upsert)
        admin = db.query(Admin).filter(Admin.email == ADMIN_EMAIL).first()
        if admin is None:
            db.add(
                Admin(
                    email=ADMIN_EMAIL,
                    hashed_password=hash_password(ADMIN_PASSWORD),
                    full_name="Royale Isles Private Office",
                )
            )
            db.commit()
            print(f"Created admin {ADMIN_EMAIL}")
        else:
            print(f"Admin {ADMIN_EMAIL} already exists — leaving as is.")

        # Content (only if there are no themes yet, to avoid clobbering admin edits)
        if db.query(Theme).count() == 0:
            for index, (title, description, traveller, encounter) in enumerate(THEMES):
                theme = Theme(
                    title=title,
                    description=description,
                    traveller=traveller,
                    encounter=encounter,
                    sort_order=index,
                )
                for p_index, place in enumerate(PLACES_BY_THEME.get(title, [])):
                    name, region, desc, lng, lat, best, activities = place
                    theme.places.append(
                        Place(
                            name=name,
                            region=region,
                            description=desc,
                            longitude=lng,
                            latitude=lat,
                            best_time=best,
                            activities=activities,
                            sort_order=p_index,
                        )
                    )
                db.add(theme)
            db.commit()
            print(f"Seeded {len(THEMES)} themes with starter places.")
        else:
            print("Themes already present — skipping content seed.")

        if db.query(Package).count() == 0:
            for package in PACKAGES:
                db.add(Package(**package))
            db.commit()
            print(f"Seeded {len(PACKAGES)} packages.")
        else:
            print("Packages already present — skipping.")

        print("\nAdmin login:")
        print(f"  email:    {ADMIN_EMAIL}")
        print(f"  password: {ADMIN_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
