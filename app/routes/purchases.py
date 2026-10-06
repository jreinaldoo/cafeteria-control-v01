from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.models import Product, Purchase
from app.services.purchase_service import create_purchase, update_purchase

purchases_bp = Blueprint("purchases", __name__)


@purchases_bp.get("/")
def index():
    purchases = Purchase.query.order_by(Purchase.purchase_date.desc(), Purchase.id.desc()).limit(100).all()
    return render_template("purchases/index.html", purchases=purchases)


@purchases_bp.route("/nova", methods=["GET", "POST"])
def new():
    products = Product.query.filter_by(active=True).order_by(Product.name).all()
    if request.method == "POST":
        try:
            purchase_date_str = request.form.get("purchase_date")
            purchase_date = datetime.strptime(purchase_date_str, "%Y-%m-%d").date() if purchase_date_str else None
            purchase = create_purchase(
                request.form["product_id"],
                request.form["quantity"],
                request.form["unit_cost"].replace(",", "."),
                request.form.get("supplier", "").strip() or None,
                purchase_date,
            )
            flash(f"Compra #{purchase.id} registrada e estoque atualizado.", "success")
            return redirect(url_for("purchases.index"))
        except (ValueError, KeyError) as exc:
            flash(str(exc), "error")
    return render_template("purchases/form.html", products=products)


@purchases_bp.route("/<int:purchase_id>/editar", methods=["GET", "POST"])
def edit(purchase_id):
    purchase = Purchase.query.get_or_404(purchase_id)
    products = Product.query.filter_by(active=True).order_by(Product.name).all()
    if request.method == "POST":
        try:
            purchase_date_str = request.form.get("purchase_date")
            purchase_date = datetime.strptime(purchase_date_str, "%Y-%m-%d").date() if purchase_date_str else None
            purchase = update_purchase(
                purchase_id,
                request.form["product_id"],
                request.form["quantity"],
                request.form["unit_cost"].replace(",", "."),
                request.form.get("supplier", "").strip() or None,
                purchase_date,
            )
            flash(f"Compra #{purchase.id} atualizada e estoque recalculado.", "success")
            return redirect(url_for("purchases.index"))
        except (ValueError, KeyError) as exc:
            flash(str(exc), "error")
    return render_template("purchases/form.html", purchase=purchase, products=products)
