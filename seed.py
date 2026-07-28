"""Seed the database with a demo traveller and itineraries.

Run once (after setting a working DATABASE_URL) with:

    python seed.py

Login credentials created:
    email:    harrison.sterling@heritage-travels.com
    password: traveller123
"""

from datetime import date

from app.database.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import Itinerary, ItineraryStop, Traveller

DEMO_EMAIL = "harrison.sterling@heritage-travels.com"
DEMO_PASSWORD = "traveller123"

DEMO_PROFILE = dict(
    full_name="Lord Harrison Sterling",
    phone="+44 20 7946 0192",
    passport_number="UK-983742-C",
    passport_expiry=date(2029, 3, 14),
    nationality="British",
    dietary_preferences="Vegetarian / No Shellfish, prefers high-tea selections",
    travel_style="Heritage Travel, Vintage Rail & Private Manors",
    emergency_contact_name="Lady Beatrice Sterling",
    emergency_contact_phone="+44 20 7946 0451",
)

DEMO_ITINERARIES = [
    {
        "id": "itinerary-1",
        "title": "The Caledonian Sleeper & Highlands Classic",
        "destination": "London to Scottish Highlands",
        "start_date": "2026-08-15",
        "end_date": "2026-08-22",
        "cover_image": "https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?auto=format&fit=crop&q=80&w=800",
        "stops": [
            {"id": "stop-1-1", "time": "21:15", "activity": "Board the Caledonian Sleeper at London Euston", "location": "London Euston Station, platform 1", "notes": "Settle into the Club Solo Suite. Welcome champagne served upon departure."},
            {"id": "stop-1-2", "time": "08:30", "activity": "Arrive in Fort William & Traditional Highland Breakfast", "location": "The Highland Cafe, Fort William", "notes": "Collect pre-arranged Range Rover Defender from the station concourse."},
            {"id": "stop-1-3", "time": "14:00", "activity": "Private Tour of Inverlochy Castle & Lake Cruise", "location": "Inverlochy Castle Hotel, Torlundy", "notes": "Check-in to the Queen Victoria Suite. Guided loch cruise with local wildlife ranger."},
            {"id": "stop-1-4", "time": "19:30", "activity": "Whisky Tasting & 5-Course Heritage Dinner", "location": "The Great Hall Dining Room", "notes": "Formal attire recommended (tweed or black tie optional). Tasting flight of vintage single malts."},
        ],
    },
    {
        "id": "itinerary-2",
        "title": "The Cotswolds Manor Estates & Private Gardens",
        "destination": "Cotswolds AONB, England",
        "start_date": "2026-09-05",
        "end_date": "2026-09-10",
        "cover_image": "https://images.unsplash.com/photo-1543872084-c7bd3822856f?auto=format&fit=crop&q=80&w=800",
        "stops": [
            {"id": "stop-2-1", "time": "10:30", "activity": "Check-in & Afternoon Botanical Tea", "location": "Barnsley House Hotel & Spa", "notes": "Relax in the historical gardens designed by Rosemary Verey."},
            {"id": "stop-2-2", "time": "15:00", "activity": "Private Antiquarian Bookshop Tour", "location": "Chipping Campden High Street", "notes": "Private consultation with bookseller Mr. Arkwright for vintage travel memoirs."},
        ],
    },
    {
        "id": "itinerary-3",
        "title": "The Ceylon Heritage Trail",
        "destination": "Colombo to the Hill Country & Southern Coast, Sri Lanka",
        "start_date": "2026-10-12",
        "end_date": "2026-10-21",
        "cover_image": "https://images.unsplash.com/photo-1586183189334-1596e293dae1?auto=format&fit=crop&q=80&w=800",
        "stops": [
            {"id": "stop-3-1", "time": "07:45", "activity": "Arrival at Bandaranaike & Colonial Colombo Walking Tour", "location": "Galle Face Green & the Dutch Hospital Precinct, Colombo", "notes": "Private car transfer waiting at arrivals. Sunset stroll along Galle Face Green, followed by a welcome dinner of Ceylonese fine dining."},
            {"id": "stop-3-2", "time": "09:00", "activity": "Sacred City of Kandy & the Temple of the Tooth Relic", "location": "Sri Dalada Maligawa, Kandy", "notes": "Modest attire required for temple grounds. Evening reserved for a traditional Kandyan dance and fire-walking performance."},
            {"id": "stop-3-3", "time": "05:30", "activity": "Sunrise Ascent of Sigiriya Rock Fortress", "location": "Sigiriya Lion Rock, Central Province", "notes": "Early departure recommended to beat the heat and crowds. Private guide will narrate the 5th-century frescoes and water gardens."},
            {"id": "stop-3-4", "time": "11:00", "activity": "Tea Estate Walk & the Nine Arches Bridge", "location": "Ella, Uva Highlands", "notes": "Guided walk through a working tea plantation with a tasting of high-grown Ceylon tea. Photograph the colonial-era viaduct at midday light."},
            {"id": "stop-3-5", "time": "16:00", "activity": "Ambalangoda Mask-Carving Workshop & Artisan Studio Visit", "location": "Ariyapala Mask Museum, Ambalangoda", "notes": "Private session with a master carver of traditional Sri Lankan devil and Kolam masks. Opportunity to commission a bespoke hand-carved piece."},
            {"id": "stop-3-6", "time": "09:00", "activity": "Galle Dutch Fort Ramparts & Boutique Antiquities Tour", "location": "Galle Fort, Southern Province", "notes": "Explore the UNESCO-listed fort walls, colonial villas, and curated antique shops along Church Street."},
        ],
    },
    {
        "id": "itinerary-4",
        "title": "The Ancient Kingdoms & Wild Coast Safari",
        "destination": "Cultural Triangle to the Deep South, Sri Lanka",
        "start_date": "2026-11-08",
        "end_date": "2026-11-16",
        "cover_image": "https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&q=80&w=800",
        "stops": [
            {"id": "stop-4-1", "time": "08:00", "activity": "Ancient City of Anuradhapura & Sacred Bodhi Tree", "location": "Sri Maha Bodhi, Anuradhapura", "notes": "Guided tour of the 3rd-century BC dagobas and monastic ruins. White or light-coloured attire respectfully requested."},
            {"id": "stop-4-2", "time": "10:30", "activity": "Royal Ruins of Polonnaruwa by Bicycle", "location": "Polonnaruwa Archaeological Museum & Gal Vihara", "notes": "Private cycling guide leads a shaded route past the medieval royal palace and rock-cut Buddha statues."},
            {"id": "stop-4-3", "time": "06:00", "activity": "Nuwara Eliya Tea Country & Highland Rail Journey", "location": "Pedro Tea Estate, Nuwara Eliya", "notes": "Board the scenic highland train through misty tea terraces. Afternoon tea served at a colonial-era planter's bungalow."},
            {"id": "stop-4-4", "time": "06:00", "activity": "Private Safari Drive in Yala National Park", "location": "Yala National Park, Southern Province", "notes": "Open-jeep safari tracking leopard, elephant, and sloth bear with a licensed naturalist. Bring neutral-toned attire."},
            {"id": "stop-4-5", "time": "06:30", "activity": "Whale Watching Excursion off the Southern Coast", "location": "Mirissa Harbour", "notes": "Private charter boat departs at dawn for blue whale and spinner dolphin sightings. Light breakfast served on board."},
            {"id": "stop-4-6", "time": "18:00", "activity": "Farewell Seafood Dinner on Bentota Beach", "location": "Bentota River Estuary, Western Coast", "notes": "Private beachfront table with a catch-of-the-day tasting menu, closing the voyage under lantern light."},
        ],
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Idempotent: remove any existing demo traveller (cascades to itineraries/stops).
        existing = db.query(Traveller).filter(Traveller.email == DEMO_EMAIL).first()
        if existing is not None:
            db.delete(existing)
            db.commit()
            print(f"Removed existing traveller {DEMO_EMAIL} before reseeding.")

        traveller = Traveller(
            email=DEMO_EMAIL,
            hashed_password=hash_password(DEMO_PASSWORD),
            **DEMO_PROFILE,
        )

        for itinerary_data in DEMO_ITINERARIES:
            stops = itinerary_data.pop("stops")
            itinerary = Itinerary(**itinerary_data)
            for index, stop in enumerate(stops):
                itinerary.stops.append(ItineraryStop(sort_order=index, **stop))
            traveller.itineraries.append(itinerary)

        db.add(traveller)
        db.commit()

        print("Seed complete.")
        print(f"  Traveller: {DEMO_PROFILE['full_name']} <{DEMO_EMAIL}>")
        print(f"  Password:  {DEMO_PASSWORD}")
        print(f"  Itineraries: {len(DEMO_ITINERARIES)}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
