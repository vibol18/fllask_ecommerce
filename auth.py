from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models import User, db

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        user = User.query.filter_by(username=username).first()
        if user is not None and user.check_password(password):
            session["user_id"] = user.id
            flash(f"Welcome back, {user.username}!", "success")
            next_url = request.form.get("next") or request.args.get("next") or ""
            if next_url.startswith("/"):
                return redirect(next_url)
            return redirect(url_for("products.index"))
        flash("Invalid username or password.", "danger")

    return render_template("auth/login.html")


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("products.index"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        confirm = request.form.get("confirm") or ""

        errors = []
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters long.")
        if not email or "@" not in email:
            errors.append("Please enter a valid email address.")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
        if password != confirm:
            errors.append("Passwords do not match.")

        if not errors:
            if User.query.filter_by(username=username).first():
                errors.append("That username is already taken.")
            elif User.query.filter_by(email=email).first():
                errors.append("That email is already registered.")

        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id
            flash("Account created — welcome to FlashShop!", "success")
            return redirect(url_for("products.index"))

    return render_template("auth/register.html")
