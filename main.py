import os

from flask import Flask, context_processor, session

from helpers import get_current_user
from models import Product, User, db


def _cart_count():
    """Count items in the session-based shopping cart."""
    cart = session.get("cart") or {}
    total = 0
    for pid_str, qty in cart.items():
        try:
            product = db.session.get(Product, int(pid_str))
        except (ValueError, TypeError):
            continue
        if product is not None:
            total += int(qty or 0)
    return total


def _seed_admin():
    if User.query.filter_by(username="admin").first() is None:
        admin = User(username="admin", email="admin@flashshop.local")
        admin.set_password(os.environ.get("ADMIN_PASSWORD") or "admin123")
        admin.is_admin = True
        db.session.add(admin)
        db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY") or "dev-secret-change-me",
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL") or "sqlite:///flashshop.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    database_url = app.config["SQLALCHEMY_DATABASE_URI"]
    if database_url.startswith("postgres://"):
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url.replace(
            "postgres://", "postgresql://", 1
        )

    db.init_app(app)

    from auth import bp as auth_bp
    from cart import bp as cart_bp
    from orders import bp as orders_bp
    from products import admin_bp, bp as products_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)

    @app.context_processor
    def inject_globals():
        return {"current_user": get_current_user(), "cart_count": _cart_count()}

    with app.app_context():
        db.create_all()
        _seed_admin()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
