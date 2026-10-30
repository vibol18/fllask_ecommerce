from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from models import Product, db

bp = Blueprint("cart", __name__, url_prefix="/cart")

CART_KEY = "cart"


def _get_cart():
    cart = session.get(CART_KEY)
    if not isinstance(cart, dict):
        cart = {}
        session[CART_KEY] = cart
    return cart


def _cart_items():
    items = []
    cart = _get_cart()
    for pid_str, qty in cart.items():
        product = db.session.get(Product, int(pid_str))
        quantity = int(qty or 0)
        if product is not None and quantity > 0 and product.stock > 0:
            items.append({"product": product, "quantity": quantity})
    return items


@bp.route("/")
def cart():
    items = _cart_items()
    total = round(sum(i["product"].price * i["quantity"] for i in items), 2)
    return render_template("cart.html", items=items, total=total)


@bp.route("/add", methods=["POST"])
def add():
    product = db.session.get(Product, int(request.form.get("product_id") or 0))
    if product is None:
        flash("Product not found.", "danger")
        return redirect(url_for("products.index"))

    quantity = int(request.form.get("quantity") or 1)
    quantity = max(1, min(quantity, product.stock or 1))

    cart = _get_cart()
    key = str(product.id)
    cart[key] = int(cart.get(key) or 0) + quantity
    flash(f"Added {quantity} x {product.name} to your cart.", "success")
    return redirect(url_for("products.detail", pid=product.id))


@bp.route("/update/<int:pid>", methods=["POST"])
def update(pid):
    product = db.session.get(Product, pid)
    if product is None:
        abort(404)

    quantity = int(request.form.get("quantity") or 1)
    cart = _get_cart()
    if quantity <= 0:
        cart.pop(str(pid), None)
    else:
        cart[str(pid)] = max(1, quantity)

    flash("Cart updated.", "success")
    return redirect(url_for("cart.cart"))


@bp.route("/remove/<int:pid>", methods=["POST"])
def remove(pid):
    cart = _get_cart()
    cart.pop(str(pid), None)
    flash("Item removed from cart.", "success")
    return redirect(url_for("cart.cart"))


@bp.route("/clear", methods=["POST"])
def clear():
    session[CART_KEY] = {}
    flash("Cart cleared.", "success")
    return redirect(url_for("cart.cart"))
