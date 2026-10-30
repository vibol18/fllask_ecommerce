from functools import wraps

from flask import abort, flash, redirect, request, session, url_for

from models import User, db


def get_current_user():
    user_id = session.get("user_id")
    if user_id is None:
        return None
    try:
        return db.session.get(User, int(user_id))
    except (ValueError, TypeError):
        return None


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if get_current_user() is None:
            flash("Please log in first.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapper


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if user is None:
            return redirect(url_for("auth.login", next=request.path))
        if not user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapper
