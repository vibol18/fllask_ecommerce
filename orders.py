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

from helpers import get_current_user, login_required
from models import Order, OrderItem, Product, db

bp = Blueprint("orders", __name__, url_prefix="/orders")

CART_KEY = "cart"


def _cart_items():
    items = []
    cart = session.get(CART_KEY) or {}
    for pid_str, qty in cart.items():
        product = db.session.get(Product, int(pid_str))
        quantity = int(qty or 0)
        if product is not None and quantity > 0 and product.stock > 0:
            items.append({"product": product, "quantity": quantity})
    return items


@bp.route("/")
@login_required
def orders():
    user = get_current_user()
    order_list = (
        Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    )
    return render_template("orders/list.html", orders=order_list)


@bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    user = get_current_user()
    items = _cart_items()
    total = round(sum(i["product"].price * i["quantity"] for i in items), 2)

    if request.method == "POST":
        if not items:
            flash("Your cart is empty.", "warning")
            return redirect(url_for("cart.cart"))

        for item in items:
            if item["quantity"] > item["product"].stock:
                flash(f"Not enough stock for {item['product'].name}.", "danger")
                return redirect(url_for("cart.cart"))

        order = Order(user_id=user.id, total=total, status="pending")
        db.session.add(order)
        db.session.flush()
        for item in items:
            db.session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=item["product"].id,
                    quantity=item["quantity"],
                    price=item["product"].price,
                )
            )
            item["product"].stock -= item["quantity"]

        db.session.commit()
        session[CART_KEY] = {}
        flash("Order placed successfully! Thank you for shopping with us.", "success")
        return redirect(url_for("orders.order_detail", oid=order.id))

    return render_template("checkout.html", items=items, total=total)


@bp.route("/<int:oid>")
@login_required
def order_detail(oid):
    order = db.session.get(Order, oid)
    if order is None:
        abort(404)

    user = get_current_user()
    if order.user_id != user.id and not user.is_admin:
        abort(403)

    items = order.items
    order_total = round(sum(i.quantity * i.price for i in items), 2)
    return render_template(
        "orders/detail.html", order=order, items=items, order_total=order_total
    )
print("hiiii")