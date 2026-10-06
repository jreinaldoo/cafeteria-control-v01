from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.models import Product, Sale
from app.services.sale_service import create_sale, update_sale

sales_bp = Blueprint("sales", __name__)


@sales_bp.get("/")
def index():
    sales = Sale.query.order_by(Sale.sale_date.desc()).limit(100).all()
    return render_template("sales/index.html", sales=sales)


@sales_bp.route("/nova", methods=["GET", "POST"])
def new():
    products = Product.query.filter_by(active=True).order_by(Product.name).all()
    if request.method == "POST":
        try:
            product_ids = request.form.getlist("product_id[]")
            quantities = request.form.getlist("quantity[]")
            items = [
                {"product_id": product_id, "quantity": quantity}
                for product_id, quantity in zip(product_ids, quantities)
                if product_id and quantity
            ]
            sale_date_str = request.form.get("sale_date")
            sale_date = datetime.strptime(sale_date_str, "%Y-%m-%d") if sale_date_str else None
            sale = create_sale(items, request.form["payment_method"], sale_date)
            flash(f"Venda #{sale.id} registrada: R$ {sale.total:.2f}.", "success")
            return redirect(url_for("sales.index"))
        except (ValueError, KeyError) as exc:
            flash(str(exc), "error")
    return render_template("sales/form.html", products=products)


@sales_bp.get("/<int:sale_id>")
def detail(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    return render_template("sales/detail.html", sale=sale)


@sales_bp.route("/<int:sale_id>/editar", methods=["GET", "POST"])
def edit(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    products = Product.query.filter_by(active=True).order_by(Product.name).all()
    if request.method == "POST":
        try:
            product_ids = request.form.getlist("product_id[]")
            quantities = request.form.getlist("quantity[]")
            items = [
                {"product_id": product_id, "quantity": quantity}
                for product_id, quantity in zip(product_ids, quantities)
                if product_id and quantity
            ]
            sale_date_str = request.form.get("sale_date")
            sale_date = datetime.strptime(sale_date_str, "%Y-%m-%d") if sale_date_str else None
            sale = update_sale(sale_id, items, request.form["payment_method"], sale_date)
            flash(f"Venda #{sale.id} atualizada: R$ {sale.total:.2f}.", "success")
            return redirect(url_for("sales.index"))
        except (ValueError, KeyError) as exc:
            flash(str(exc), "error")
    return render_template("sales/form.html", sale=sale, products=products)
