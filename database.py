
"""SQLite helper functions for the Pet Adoption Portal."""

import os
import sqlite3
from contextlib import closing

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get(
    "DATABASE_PATH",
    os.path.join(BASE_DIR, "database", "pets.db")
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

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
    status TEXT NOT NULL DEFAULT 'Available',
    owner_id INTEGER,
    FOREIGN KEY (owner_id) REFERENCES users (id)
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
    applicant_id INTEGER,
    FOREIGN KEY (pet_id) REFERENCES pets (id),
    FOREIGN KEY (applicant_id) REFERENCES users (id)
);
"""

SAMPLE_PETS = [
    (
        "Bruno", "Dog", "Labrador", 2, "Male", "Pune",
        "Bruno is a playful, friendly Labrador who loves fetch "
        "and long walks. Great with kids."
    ),
    (
        "Milo", "Cat", "Persian", 1, "Male", "Mumbai",
        "Milo is a calm Persian cat with a fluffy coat. "
        "He enjoys naps in sunny spots."
    ),
    (
        "Rocky", "Dog", "Beagle", 3, "Male", "Nashik",
        "Rocky is an energetic Beagle with a great nose. "
        "He needs an active family."
    ),
    (
        "Bella", "Dog", "Golden Retriever", 2, "Female", "Pune",
        "Bella is a gentle Golden Retriever who is friendly "
        "with everyone she meets."
    ),
    (
        "Simba", "Cat", "Indian Cat", 1, "Male", "Mumbai",
        "Simba is a curious, cuddly kitten who loves to explore "
        "and play."
    ),
]


def get_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create tables and safely add new columns to existing databases."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    with closing(get_connection()) as conn:
        conn.executescript(SCHEMA)

        # Migrate existing databases without deleting their data.
        pet_columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(pets)")
        }
        if "owner_id" not in pet_columns:
            conn.execute(
                "ALTER TABLE pets ADD COLUMN owner_id INTEGER "
                "REFERENCES users(id)"
            )

        adoption_columns = {
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(adoption_requests)"
            )
        }
        if "applicant_id" not in adoption_columns:
            conn.execute(
                "ALTER TABLE adoption_requests ADD COLUMN "
                "applicant_id INTEGER REFERENCES users(id)"
            )

        pet_count = conn.execute(
            "SELECT COUNT(*) FROM pets"
        ).fetchone()[0]

        if pet_count == 0:
            conn.executemany(
                "INSERT INTO pets "
                "(name, type, breed, age, gender, location, description) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                SAMPLE_PETS
            )

        conn.commit()


# ---------- users ----------

def create_user(name, email, password_hash):
    """Create a new user and return the user's ID."""
    with closing(get_connection()) as conn:
        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash) "
            "VALUES (?, ?, ?)",
            (name, email.lower().strip(), password_hash)
        )
        conn.commit()
        return cur.lastrowid


def get_user_by_email(email):
    """Find a user by email address."""
    with closing(get_connection()) as conn:
        return conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email.lower().strip(),)
        ).fetchone()


def get_user(user_id):
    """Find a user by ID."""
    with closing(get_connection()) as conn:
        return conn.execute(
            "SELECT id, name, email, created_at "
            "FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()


# ---------- pets ----------

def add_pet(
    name, pet_type, breed, age, gender, location,
    description, image_url, owner_id=None
):
    """Add a pet listing and optionally link it to its owner."""
    with closing(get_connection()) as conn:
        cur = conn.execute(
            "INSERT INTO pets "
            "(name, type, breed, age, gender, location, description, "
            "image_url, owner_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                name, pet_type, breed, age, gender, location,
                description, image_url, owner_id
            )
        )
        conn.commit()
        return cur.lastrowid


def get_pets(search="", pet_type="", location="", status=None):
    """Return pet listings with optional filters."""
    query = "SELECT * FROM pets WHERE 1=1"
    params = []

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
        return conn.execute(
            query + " ORDER BY id DESC", params
        ).fetchall()


def get_pet(pet_id):
    """Return a pet by its ID."""
    with closing(get_connection()) as conn:
        return conn.execute(
            "SELECT * FROM pets WHERE id = ?",
            (pet_id,)
        ).fetchone()


def get_user_pets(owner_id):
    """Return listings belonging to a particular user."""
    with closing(get_connection()) as conn:
        return conn.execute(
            "SELECT * FROM pets WHERE owner_id = ? ORDER BY id DESC",
            (owner_id,)
        ).fetchall()


def get_locations():
    """Return all distinct pet locations."""
    with closing(get_connection()) as conn:
        rows = conn.execute(
            "SELECT DISTINCT location FROM pets ORDER BY location"
        ).fetchall()
        return [row["location"] for row in rows]


def update_pet_status(pet_id, status, owner_id=None):
    """Update a listing's status, optionally checking its owner."""
    with closing(get_connection()) as conn:
        if owner_id is None:
            cur = conn.execute(
                "UPDATE pets SET status = ? WHERE id = ?",
                (status, pet_id)
            )
        else:
            cur = conn.execute(
                "UPDATE pets SET status = ? "
                "WHERE id = ? AND owner_id = ?",
                (status, pet_id, owner_id)
            )

        conn.commit()
        return cur.rowcount > 0


# ---------- adoption requests ----------

def add_adoption_request(
    pet_id, applicant_name, email, phone, reason,
    applicant_id=None
):
    """Save an adoption request, optionally linking the applicant."""
    with closing(get_connection()) as conn:
        cur = conn.execute(
            "INSERT INTO adoption_requests "
            "(pet_id, applicant_name, email, phone, reason, applicant_id) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                pet_id, applicant_name, email, phone,
                reason, applicant_id
            )
        )
        conn.commit()
        return cur.lastrowid


def get_adoption_requests():
    """Return all adoption requests with their pet names."""
    with closing(get_connection()) as conn:
        return conn.execute(
            "SELECT r.*, p.name AS pet_name "
            "FROM adoption_requests r "
            "JOIN pets p ON p.id = r.pet_id "
            "ORDER BY r.id DESC"
        ).fetchall()


def get_user_adoption_requests(user_id):
    """Return adoption requests submitted by a user."""
    with closing(get_connection()) as conn:
        return conn.execute(
            "SELECT r.*, p.name AS pet_name "
            "FROM adoption_requests r "
            "JOIN pets p ON p.id = r.pet_id "
            "WHERE r.applicant_id = ? ORDER BY r.id DESC",
            (user_id,)
        ).fetchall()


def get_owner_adoption_requests(owner_id):
    """Return requests for pets listed by a particular owner."""
    with closing(get_connection()) as conn:
        return conn.execute(
            "SELECT r.*, p.name AS pet_name "
            "FROM adoption_requests r "
            "JOIN pets p ON p.id = r.pet_id "
            "WHERE p.owner_id = ? ORDER BY r.id DESC",
            (owner_id,)
        ).fetchall()
