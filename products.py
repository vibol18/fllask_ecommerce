from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from helpers import admin_required
from models import Order, Product, User, db

bp = Blueprint("products", __name__, url_prefix="/products")
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _to_float(value):
    try:
        return float(value or 0)
    except (ValueError, TypeError):
        return 0.0


def _to_int(value):
    try:
        return int(float(value or 0))
    except (ValueError, TypeError):
        return 0


@bp.route("/")
def index():
    q = (request.args.get("q") or "").strip()
    category = (request.args.get("category") or "").strip()
    query = Product.query
    if category:
        query = query.filter(Product.category == category)
    if q:
        like_pattern = f"%{q}%"
        query = query.filter(
            Product.name.ilike(like_pattern) | Product.description.ilike(like_pattern)
        )
    products = query.order_by(Product.created_at.desc()).all()
    categories = [
        row[0] for row in db.session.query(Product.category).distinct().all() if row[0]
    ]
    return render_template(
        "index.html",
        products=products,
        categories=categories,
        q=q,
        selected_category=category,
    )


@bp.route("/<int:pid>")
def detail(pid):
    product = db.session.get(Product, pid)
    if product is None:
        abort(404)
    return render_template("product.html", product=product)


# ------------------------------------------------------------------ Admin


@admin_bp.route("/")
@admin_required
def dashboard():
    product_count = Product.query.count()
    user_count = User.query.count()
    order_count = Order.query.count()
    revenue = db.session.query(db.func.sum(Order.total)).scalar()
    revenue = round(float(revenue or 0), 2)
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(6).all()
    low_stock = Product.query.filter(Product.stock < 5).order_by(Product.stock.asc()).all()
    return render_template(
        "admin/dashboard.html",
        product_count=product_count,
        user_count=user_count,
        order_count=order_count,
        revenue=revenue,
        recent_orders=recent_orders,
        low_stock=low_stock,
    )


@admin_bp.route("/products")
@admin_required
def admin_products():
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template("admin/products.html", products=products)


@admin_bp.route("/products/new", methods=["GET", "POST"])
@admin_required
def admin_product_new():
    if request.method == "POST":
        product = Product(
            name=request.form.get("name", "").strip(),
            category=(request.form.get("category") or "General").strip() or "General",
            price=_to_float(request.form.get("price")),
            stock=_to_int(request.form.get("stock")),
            image_url=(request.form.get("image_url") or "").strip(),
            description=request.form.get("description") or "",
        )
        if not product.name:
            flash("Product name is required.", "danger")
        else:
            db.session.add(product)
            db.session.commit()
            flash("Product created.", "success")
            return redirect(url_for("admin.admin_products"))
    return render_template("admin/product_form.html", product=None)


@admin_bp.route("/products/<int:pid>/edit", methods=["GET", "POST"])
@admin_required
def admin_product_edit(pid):
    product = db.session.get(Product, pid)
    if product is None:
        abort(404)
    if request.method == "POST":
        product.name = request.form.get("name", "").strip()
        product.category = (request.form.get("category") or "General").strip() or "General"
        product.price = _to_float(request.form.get("price"))
        product.stock = _to_int(request.form.get("stock"))
        product.image_url = (request.form.get("image_url") or "").strip()
        product.description = request.form.get("description") or ""
        product.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Product updated.", "success")
        return redirect(url_for("admin.admin_products"))
    return render_template("admin/product_form.html", product=product)


@admin_bp.route("/products/<int:pid>/delete", methods=["POST"])
@admin_required
def admin_product_delete(pid):
    product = db.session.get(Product, pid)
    if product is None:
        abort(404)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted.", "success")
    return redirect(url_for("admin.admin_products"))
