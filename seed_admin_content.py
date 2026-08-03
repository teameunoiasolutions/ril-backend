"""Seed an admin account and the initial site content (themes, places, packages).

Run once (after a working DATABASE_URL) with:

    python seed_admin_content.py

Admin login created:
    email:    admin@royaleisles.lk
    password: admin12345
"""

from app.database.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import Admin, Package, Place, Theme, ThemePackage

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

# The two sub-packages sold under every theme on the Designed Trips flow.
# "The Glimpse" is 2 days / half; "The Immersion" is 4 days / full. The hotel
# and activities here are the locked inclusions the traveller cannot edit.
THEME_PACKAGES_BY_THEME = {
    "Wildlife & Wilderness": [
        {
            "tier": "glimpse", "name": "The Glimpse", "days": 2, "coverage": "half", "price_add": 780,
            "summary": "Two dawn drives in leopard country, with the afternoons left to the lodge veranda.",
            "hotel": "Wild Coast Tented Lodge, Yala",
            "activities": ["A private dawn safari in Yala Block I", "An evening waterhole drive", "A naturalist's briefing over dinner"],
            "inclusions": ["Two nights, cocoon suite", "Park fees and private jeep", "Resident naturalist throughout", "All meals and soft drinks"],
        },
        {
            "tier": "immersion", "name": "The Immersion", "days": 4, "coverage": "full", "price_add": 1960,
            "summary": "Four days across two wildernesses — Yala's leopards and Wilpattu's quieter, older forest.",
            "hotel": "Wild Coast Tented Lodge, Yala & Leopard Trails Camp, Wilpattu",
            "activities": ["Full-day Yala leopard tracking", "Wilpattu villu circuit with a field researcher", "A night-sound walk with the camp naturalist", "Elephant gathering at Minneriya (seasonal)"],
            "inclusions": ["Four nights across two camps", "All park fees and private jeeps", "Dedicated naturalist and tracker", "All meals, wines and camp transfers"],
        },
    ],
    "Ocean & Discovery": [
        {
            "tier": "glimpse", "name": "The Glimpse", "days": 2, "coverage": "half", "price_add": 640,
            "summary": "A blue-whale morning off Mirissa, then the coast at its own unhurried pace.",
            "hotel": "Cape Weligama, Southern Coast",
            "activities": ["A private whale-watching charter at first light", "An afternoon on the cliff-edge pool", "Sunset supper by the sea"],
            "inclusions": ["Two nights, ocean-view villa", "Private charter and marine guide", "Breakfast and one supper", "Coastal transfers"],
        },
        {
            "tier": "immersion", "name": "The Immersion", "days": 4, "coverage": "full", "price_add": 1680,
            "summary": "Four days of open water — whales, a sailing day, and the lagoons most travellers never see.",
            "hotel": "Cape Weligama & Amanwella, Tangalle",
            "activities": ["Blue-whale charter with a marine biologist", "A full sailing day along the southern bays", "Kayaking the Rekawa lagoon at dusk", "Turtle-nesting watch with a conservation ranger"],
            "inclusions": ["Four nights across two properties", "All charters, skipper and marine guide", "All meals and a private beach supper", "Conservation contribution included"],
        },
    ],
    "Heritage & Memory": [
        {
            "tier": "glimpse", "name": "The Glimpse", "days": 2, "coverage": "half", "price_add": 720,
            "summary": "Sigiriya before the gates open, and Dambulla's cave ceilings in the cool of the day.",
            "hotel": "Water Garden Sigiriya",
            "activities": ["The Sigiriya dawn ascent, ahead of the crowds", "The Dambulla cave temples with a resident scholar", "An evening of village cooking"],
            "inclusions": ["Two nights, garden villa", "Private dawn access and site fees", "Resident-scholar accompaniment", "All meals"],
        },
        {
            "tier": "immersion", "name": "The Immersion", "days": 4, "coverage": "full", "price_add": 1840,
            "summary": "Four days through three ancient capitals, read slowly and in the right order.",
            "hotel": "Water Garden Sigiriya & Ulagalla, Anuradhapura",
            "activities": ["The Sigiriya dawn ascent", "Anuradhapura's sacred precinct and Bodhi Tree", "Polonnaruwa by bicycle at dawn", "A private evening at the Temple of the Tooth"],
            "inclusions": ["Four nights across two properties", "All site fees and private access", "Archaeologist accompaniment throughout", "All meals and inter-site transfers"],
        },
    ],
    "Wellness & Restoration": [
        {
            "tier": "glimpse", "name": "The Glimpse", "days": 2, "coverage": "half", "price_add": 590,
            "summary": "Two days of Ayurvedic mornings and long, uninterrupted afternoons.",
            "hotel": "Santani Wellness, Kandy",
            "activities": ["A physician's Ayurvedic consultation", "Two guided treatment mornings", "Sunrise yoga above the valley"],
            "inclusions": ["Two nights, valley-view chalet", "Consultation and prescribed treatments", "Full wellness cuisine", "Daily yoga and meditation"],
        },
        {
            "tier": "immersion", "name": "The Immersion", "days": 4, "coverage": "full", "price_add": 1520,
            "summary": "A four-day prescribed programme — long enough for the treatments to actually work.",
            "hotel": "Santani Wellness, Kandy",
            "activities": ["A full Ayurvedic assessment and personal programme", "Daily panchakarma treatments", "Forest-bathing and silent walking", "A herbal-garden morning with the resident physician"],
            "inclusions": ["Four nights, valley-view chalet", "Complete prescribed treatment course", "All wellness cuisine and herbal preparations", "Take-home preparations and follow-up notes"],
        },
    ],
    "Rail & Landscape": [
        {
            "tier": "glimpse", "name": "The Glimpse", "days": 2, "coverage": "half", "price_add": 540,
            "summary": "The Kandy–Ella leg in a reserved observation carriage, and a tea estate at the end of it.",
            "hotel": "98 Acres Resort, Ella",
            "activities": ["The Nanu Oya–Ella rail leg, reserved seating", "A private tea-estate walk and tasting", "Nine Arches Bridge at first light"],
            "inclusions": ["Two nights, estate chalet", "Reserved observation-carriage seats", "Estate tour and tasting", "Breakfast and one estate lunch"],
        },
        {
            "tier": "immersion", "name": "The Immersion", "days": 4, "coverage": "full", "price_add": 1440,
            "summary": "The full hill-country line, ridden in stages, with a planter's bungalow at each pause.",
            "hotel": "Ceylon Tea Trails, Bogawantalawa & 98 Acres Resort, Ella",
            "activities": ["The complete Kandy–Ella line, ridden in two stages", "A tea-estate bungalow stay with a resident planter", "Plucking and factory morning with an estate manager", "Highland walking on the Horton Plains escarpment"],
            "inclusions": ["Four nights across two bungalows", "All reserved rail seating and transfers", "Private estate access and tastings", "All meals, afternoon teas and house drinks"],
        },
    ],
    "Culture & Human Connection": [
        {
            "tier": "glimpse", "name": "The Glimpse", "days": 2, "coverage": "half", "price_add": 610,
            "summary": "Two days in Kandy — a dance rehearsal, a temple ritual, and a family kitchen.",
            "hotel": "Kings Pavilion, Kandy",
            "activities": ["A private Kandyan dance rehearsal", "The evening puja at the Temple of the Tooth", "A family kitchen and market morning"],
            "inclusions": ["Two nights, heritage suite", "Private introductions and interpreter", "Temple access and offerings", "All meals"],
        },
        {
            "tier": "immersion", "name": "The Immersion", "days": 4, "coverage": "full", "price_add": 1580,
            "summary": "Four days with the people who keep the crafts alive — artisans, musicians and their workshops.",
            "hotel": "Kings Pavilion, Kandy & Wallawwa, Colombo",
            "activities": ["A private Kandyan dance rehearsal and drum lesson", "A mask-carver's workshop in Ambalangoda", "A silversmith's studio afternoon in Kandy", "A village cooking day with a family, start to finish"],
            "inclusions": ["Four nights across two properties", "All artisan fees and materials", "Dedicated interpreter throughout", "All meals and a farewell supper"],
        },
    ],
    "Shared Heritage": [
        {
            "tier": "glimpse", "name": "The Glimpse", "days": 2, "coverage": "half", "price_add": 560,
            "summary": "Galle Fort's ramparts and a hill-station afternoon — two days of borrowed architecture.",
            "hotel": "Amangalla, Galle Fort",
            "activities": ["A Galle Fort rampart walk with a historian", "The Dutch Reformed Church and archive", "Colonial-era afternoon tea on the veranda"],
            "inclusions": ["Two nights, chamber suite", "Historian-led walking tour", "Archive and museum access", "Breakfast and afternoon tea"],
        },
        {
            "tier": "immersion", "name": "The Immersion", "days": 4, "coverage": "full", "price_add": 1500,
            "summary": "Four days reading the island's shared chapter — fort towns, hill stations and old gardens.",
            "hotel": "Amangalla, Galle Fort & Grand Hotel, Nuwara Eliya",
            "activities": ["Galle Fort ramparts, archive and church", "Nuwara Eliya's hill-station architecture and old gardens", "The Colombo civic and Cinnamon Gardens circuit", "A private library afternoon with a resident historian"],
            "inclusions": ["Four nights across two heritage properties", "Historian accompaniment throughout", "All archive, museum and garden access", "All meals and afternoon teas"],
        },
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
    {
        "name": "Coastal Serenity", "numeral": "IV", "duration": "8 Days",
        "character": "Slow mornings by the sea, cinnamon gardens, and quiet fortified towns — the southern coast read at the pace of the tide.",
        "route": ["Colombo", "Bentota", "Galle", "Weligama", "Mirissa", "Tangalle", "Airport"],
        "inclusions": ["A private villa on the southern coast", "Galle Fort at golden hour", "A dawn whale-watching charter", "A cinnamon estate visit", "Sunset suppers by the sea"],
        "pace": "Gentle", "best_for": "Coastal escapes and honeymoons", "reach": "Western & Southern coast", "price_from": 4200, "sort_order": 3,
    },
    {
        "name": "Highland Retreat", "numeral": "V", "duration": "7 Days",
        "character": "Misted tea country, cool verandas, and the slow work of restoration — hill stations and gardens reached by scenic mountain rail.",
        "route": ["Colombo", "Kandy", "Nuwara Eliya", "Ella", "Haputale", "Airport"],
        "inclusions": ["A tea-estate bungalow stay", "The scenic highland rail journey", "Private tea tastings", "Ayurvedic wellness mornings", "Nine Arches Bridge at first light"],
        "pace": "Restorative", "best_for": "Wellness and cool-climate travel", "reach": "Central Highlands & Uva", "price_from": 3900, "sort_order": 4,
    },
    {
        "name": "Wild Encounters", "numeral": "VI", "duration": "9 Days",
        "character": "Leopard country, elephant gatherings, and dawn safaris with naturalists who know when not to speak — wilderness held with patience.",
        "route": ["Colombo", "Wilpattu National Park", "Sigiriya", "Minneriya", "Kandy", "Udawalawe", "Yala", "Airport"],
        "inclusions": ["Private leopard safaris in Yala", "The Minneriya elephant gathering", "A naturalist-led field morning", "Wilpattu wilderness drives", "A tented wild-coast retreat"],
        "pace": "Adventurous", "best_for": "Wildlife and photography", "reach": "North-West, Centre & Deep South", "price_from": 5600, "sort_order": 5,
    },
    {
        "name": "Sacred Circuit", "numeral": "VII", "duration": "11 Days",
        "character": "Ancient capitals, cave temples, and living ritual — the island's spiritual heart entered slowly, with scholarship and protected timing.",
        "route": ["Colombo", "Anuradhapura", "Mihintale", "Polonnaruwa", "Sigiriya", "Dambulla", "Kandy", "Airport"],
        "inclusions": ["Private dawn access at Sigiriya", "The Dambulla cave temples", "The Temple of the Tooth", "Resident-scholar accompaniment", "A Kandyan dance and ritual evening"],
        "pace": "Contemplative", "best_for": "Heritage and scholarship", "reach": "Cultural Triangle & Central", "price_from": 6100, "sort_order": 6,
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

        # Theme sub-packages (The Glimpse / The Immersion). Added per theme and
        # matched by tier, so re-running fills gaps without duplicating or
        # clobbering anything the admin has edited.
        added_subpackages = 0
        for title, sub_packages in THEME_PACKAGES_BY_THEME.items():
            theme = db.query(Theme).filter(Theme.title == title).first()
            if theme is None:
                print(f"  Theme '{title}' not found — skipping its sub-packages.")
                continue
            existing_tiers = {
                tier
                for (tier,) in db.query(ThemePackage.tier)
                .filter(ThemePackage.theme_id == theme.id)
                .all()
            }
            for index, sub_package in enumerate(sub_packages):
                if sub_package["tier"] in existing_tiers:
                    continue
                db.add(ThemePackage(theme_id=theme.id, sort_order=index, **sub_package))
                added_subpackages += 1
        db.commit()
        print(f"Added {added_subpackages} new theme sub-package(s).")

        # Add any packages that aren't already present (matched by name), so
        # re-running the seed introduces new packages without duplicating or
        # clobbering ones the admin may have edited.
        existing_names = {name for (name,) in db.query(Package.name).all()}
        added = 0
        for package in PACKAGES:
            if package["name"] not in existing_names:
                db.add(Package(**package))
                added += 1
        db.commit()
        print(f"Added {added} new package(s); {len(existing_names)} already present.")

        print("\nAdmin login:")
        print(f"  email:    {ADMIN_EMAIL}")
        print(f"  password: {ADMIN_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
