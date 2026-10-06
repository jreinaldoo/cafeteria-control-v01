from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.models import Product, StockMovement
from app.services.stock_service import adjust_stock

stock_bp = Blueprint("stock", __name__)


@stock_bp.get("/")
def index():
    products = Product.query.filter_by(active=True).order_by(Product.name).all()
    return render_template("stock/index.html", products=products)


@stock_bp.route("/ajuste", methods=["GET", "POST"])
def adjustment():
    products = Product.query.filter_by(active=True).order_by(Product.name).all()
    if request.method == "POST":
        try:
            quantity = request.form["quantity"].replace(",", ".")
            adjust_stock(request.form["product_id"], quantity, request.form.get("notes", "").strip() or None)
            flash("Estoque ajustado.", "success")
            return redirect(url_for("stock.index"))
        except ValueError as exc:
            flash(str(exc), "error")
    return render_template("stock/adjustment.html", products=products)
