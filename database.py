"""SQLite helper functions for the Pet Adoption Portal."""
import os
import sqlite3
from contextlib import closing

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "database", "pets.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS pets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    breed TEXT NOT NULL,
    age INTEGER NOT NULL,
    gender TEXT NOT NULL,
    location TEXT NOT NULL,
    description TEXT,
    image_url TEXT,
    status TEXT NOT NULL DEFAULT 'Available'
);
CREATE TABLE IF NOT EXISTS adoption_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_id INTEGER NOT NULL,
    applicant_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    reason TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pending',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pet_id) REFERENCES pets (id)
);
"""

SAMPLE_PETS = [
    ("Bruno", "Dog", "Labrador", 2, "Male", "Pune",
     "Bruno is a playful, friendly Labrador who loves fetch and long walks. Great with kids."),
    ("Milo", "Cat", "Persian", 1, "Male", "Mumbai",
     "Milo is a calm Persian cat with a fluffy coat. He enjoys naps in sunny spots."),
    ("Rocky", "Dog", "Beagle", 3, "Male", "Nashik",
     "Rocky is an energetic Beagle with a great nose. He needs an active family."),
    ("Bella", "Dog", "Golden Retriever", 2, "Female", "Pune",
     "Bella is a gentle Golden Retriever who is friendly with everyone she meets."),
    ("Simba", "Cat", "Indian Cat", 1, "Male", "Mumbai",
     "Simba is a curious, cuddly kitten who loves to explore and play."),
]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the database and tables, and add sample pets on first run."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with closing(get_connection()) as conn:
        conn.executescript(SCHEMA)
        if conn.execute("SELECT COUNT(*) FROM pets").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO pets (name, type, breed, age, gender, location, description) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)", SAMPLE_PETS)
        conn.commit()


def add_pet(name, pet_type, breed, age, gender, location, description, image_url):
    with closing(get_connection()) as conn:
        cur = conn.execute(
            "INSERT INTO pets (name, type, breed, age, gender, location, description, image_url) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (name, pet_type, breed, age, gender, location, description, image_url))
        conn.commit()
        return cur.lastrowid


def get_pets(search="", pet_type="", location="", status=None):
    query, params = "SELECT * FROM pets WHERE 1=1", []
    if search:
        query += " AND name LIKE ?"
        params.append(f"%{search}%")
    if pet_type:
        query += " AND type = ?"
        params.append(pet_type)
    if location:
        query += " AND location = ?"
        params.append(location)
    if status:
        query += " AND status = ?"
        params.append(status)
    with closing(get_connection()) as conn:
        return conn.execute(query + " ORDER BY id DESC", params).fetchall()


def get_pet(pet_id):
    with closing(get_connection()) as conn:
        return conn.execute("SELECT * FROM pets WHERE id = ?", (pet_id,)).fetchone()


def get_locations():
    with closing(get_connection()) as conn:
        rows = conn.execute("SELECT DISTINCT location FROM pets ORDER BY location").fetchall()
    return [r["location"] for r in rows]


def add_adoption_request(pet_id, applicant_name, email, phone, reason):
    with closing(get_connection()) as conn:
        cur = conn.execute(
            "INSERT INTO adoption_requests (pet_id, applicant_name, email, phone, reason) "
            "VALUES (?, ?, ?, ?, ?)", (pet_id, applicant_name, email, phone, reason))
        conn.commit()
        return cur.lastrowid


def get_adoption_requests():
    with closing(get_connection()) as conn:
        return conn.execute(
            "SELECT r.*, p.name AS pet_name FROM adoption_requests r "
            "JOIN pets p ON p.id = r.pet_id ORDER BY r.id DESC").fetchall()
