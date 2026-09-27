
"""Pet Adoption Portal - Flask application. Project Owner: Rohan Uttekar."""

import os
import re
import sqlite3
from functools import wraps

from flask import (
    Flask, abort, flash, jsonify, redirect, render_template,
    request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

import database as db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

PET_TYPES = ["Dog", "Cat", "Rabbit", "Bird", "Other"]
GENDERS = ["Male", "Female"]
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^[0-9+\-\s()]{7,15}$")

db.init_db()


@app.context_processor
def inject_globals():
    commit = os.environ.get("RENDER_GIT_COMMIT", "")[:7]
    user = None
    if session.get("user_id"):
        user = db.get_user(session["user_id"])
    return {
        "commit": commit or "local",
        "owner": "Rohan Uttekar",
        "current_user": user,
    }


@app.template_filter("emoji")
def emoji_filter(pet_type):
    return {
        "Dog": "🐶",
        "Cat": "🐱",
        "Rabbit": "🐰",
        "Bird": "🐦",
    }.get(pet_type, "🐾")


def login_required(view):
    """Require a signed-in user to access a page."""

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to continue.", "error")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped_view


def safe_next_url(target):
    """Allow only local relative redirect paths."""
    if target and target.startswith("/") and not target.startswith("//"):
        return target
    return url_for("dashboard")


# ---------- validation ----------

def validate_pet(form):
    data = {
        k: form.get(k, "").strip()
        for k in (
            "name", "type", "breed", "age", "gender",
            "location", "description", "image_url"
        )
    }
    errors = []

    if not 2 <= len(data["name"]) <= 50:
        errors.append("Pet name must be 2-50 characters.")
    if data["type"] not in PET_TYPES:
        errors.append("Please choose a valid pet type.")
    if not 2 <= len(data["breed"]) <= 50:
        errors.append("Breed must be 2-50 characters.")
    if not (data["age"].isdigit() and 0 <= int(data["age"]) <= 30):
        errors.append("Age must be a whole number between 0 and 30.")
    if data["gender"] not in GENDERS:
        errors.append("Please choose a gender.")
    if not 2 <= len(data["location"]) <= 50:
        errors.append("Location must be 2-50 characters.")
    if len(data["description"]) > 500:
        errors.append("Description can be at most 500 characters.")
    if data["image_url"] and not re.match(
        r"^https?://\S+$", data["image_url"]
    ):
        errors.append("Image URL must start with http:// or https://.")

    return data, errors


def validate_adoption(form):
    data = {
        k: form.get(k, "").strip()
        for k in ("applicant_name", "email", "phone", "reason")
    }
    errors = []

    if not 2 <= len(data["applicant_name"]) <= 60:
        errors.append("Name must be 2-60 characters.")
    if not EMAIL_RE.match(data["email"]):
        errors.append("Please enter a valid email address.")
    if not PHONE_RE.match(data["phone"]):
        errors.append("Please enter a valid phone number (7-15 digits).")
    if not 10 <= len(data["reason"]) <= 500:
        errors.append("Reason must be 10-500 characters.")

    return data, errors


def get_pet_or_404(pet_id):
    pet = db.get_pet(pet_id)
    if pet is None:
        abort(404)
    return pet


# ---------- authentication ----------

@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))

    data = {"name": "", "email": ""}
    if request.method == "POST":
        data["name"] = request.form.get("name", "").strip()
        data["email"] = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        errors = []

        if not 2 <= len(data["name"]) <= 60:
            errors.append("Name must be 2-60 characters.")
        if not EMAIL_RE.match(data["email"]):
            errors.append("Please enter a valid email address.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if password != confirm_password:
            errors.append("Passwords do not match.")

        if not errors and db.get_user_by_email(data["email"]):
            errors.append("An account with this email already exists.")

        if not errors:
            try:
                user_id = db.create_user(
                    data["name"],
                    data["email"],
                    generate_password_hash(password)
                )
            except sqlite3.IntegrityError:
                errors.append("An account with this email already exists.")
            except sqlite3.Error:
                app.logger.exception("Could not register user")
                errors.append("Registration failed. Please try again.")
            else:
                session.clear()
                session["user_id"] = user_id
                flash("Account created successfully!", "success")
                return redirect(url_for("dashboard"))

        for error in errors:
            flash(error, "error")

    return render_template("register.html", data=data)


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = db.get_user_by_email(email)

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            flash("You are now logged in.", "success")
            return redirect(safe_next_url(request.args.get("next")))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


# ---------- pages ----------

@app.route("/")
def index():
    return render_template(
        "index.html",
        pets=db.get_pets(status="Available")[:6]
    )


@app.route("/pets")
def pets():
    search = request.args.get("search", "").strip()
    pet_type = request.args.get("type", "")
    location = request.args.get("location", "")

    return render_template(
        "pets.html",
        pets=db.get_pets(
            search, pet_type, location, status="Available"
        ),
        search=search,
        selected_type=pet_type,
        selected_location=location,
        pet_types=PET_TYPES,
        locations=db.get_locations()
    )


@app.route("/pets/<int:pet_id>")
def pet_details(pet_id):
    return render_template(
        "pet_details.html",
        pet=get_pet_or_404(pet_id)
    )


@app.route("/add-pet", methods=["GET", "POST"])
@login_required
def add_pet():
    data = {}

    if request.method == "POST":
        data, errors = validate_pet(request.form)

        if not errors:
            try:
                db.add_pet(
                    data["name"],
                    data["type"],
                    data["breed"],
                    int(data["age"]),
                    data["gender"],
                    data["location"],
                    data["description"],
                    data["image_url"],
                    owner_id=session["user_id"]
                )
            except sqlite3.Error:
                app.logger.exception("Could not save pet")
                errors.append(
                    "Something went wrong while saving. Please try again."
                )
            else:
                flash(
                    f"{data['name']} was added successfully!",
                    "success"
                )
                return redirect(url_for("dashboard"))

        for error in errors:
            flash(error, "error")

    return render_template(
        "add_pet.html",
        data=data,
        pet_types=PET_TYPES,
        genders=GENDERS
    )


@app.route("/adopt/<int:pet_id>", methods=["GET", "POST"])
@login_required
def adopt(pet_id):
    pet = get_pet_or_404(pet_id)

    if pet["status"] != "Available":
        flash(
            f"{pet['name']} is no longer available for adoption.",
            "error"
        )
        return redirect(url_for("pets"))

    data = {}
    if request.method == "POST":
        data, errors = validate_adoption(request.form)

        if not errors:
            try:
                db.add_adoption_request(
                    pet_id,
                    **data,
                    applicant_id=session["user_id"]
                )
            except sqlite3.Error:
                app.logger.exception("Could not save adoption request")
                errors.append(
                    "Something went wrong while saving. Please try again."
                )
            else:
                flash(
                    "Adoption request submitted successfully!",
                    "success"
                )
                return redirect(url_for("dashboard"))

        for error in errors:
            flash(error, "error")

    return render_template("adopt.html", pet=pet, data=data)


@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    return render_template(
        "dashboard.html",
        user=db.get_user(user_id),
        pets=db.get_user_pets(user_id),
        my_requests=db.get_user_adoption_requests(user_id),
        received_requests=db.get_owner_adoption_requests(user_id)
    )


@app.route("/adoptions")
@login_required
def adoptions():
    user_id = session["user_id"]

    # Show only requests submitted by this user.
    requests_list = db.get_user_adoption_requests(user_id)

    return render_template(
        "adoptions.html",
        requests=requests_list
    )


@app.route("/about")
def about():
    return render_template("about.html")


# ---------- API & health ----------

@app.route("/api/pets")
def api_pets():
    return jsonify([
        dict(p) for p in db.get_pets()
    ])


@app.route("/api/adoptions")
@login_required
def api_adoptions():
    """Return only adoption requests submitted by the signed-in user."""
    requests_list = db.get_user_adoption_requests(session["user_id"])
    return jsonify([
        {
            "id": r["id"],
            "pet_id": r["pet_id"],
            "pet_name": r["pet_name"],
            "status": r["status"],
            "created_at": r["created_at"]
        }
        for r in requests_list
    ])


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.errorhandler(404)
def not_found(_error):
    return render_template("error.html"), 404


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG") == "1"
    )
