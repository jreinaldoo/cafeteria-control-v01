from datetime import date, datetime
from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.models import Category, Product, Production
from app.services.production_service import (
    create_production,
    finalize_production,
    get_open_production,
    get_production_by_date,
    update_production,
)

production_bp = Blueprint("production", __name__)


@production_bp.get("/")
def index():
    productions = Production.query.order_by(Production.production_date.desc()).limit(30).all()
    open_production = get_open_production()
    return render_template("production/index.html", productions=productions, open_production=open_production)


@production_bp.route("/nova", methods=["GET", "POST"])
def new():
    # Filtrar apenas produtos que não são bebidas (assumindo que bebidas estão em categoria "Bebidas")
    products = (
        Product.query.join(Category)
        .filter(Product.active.is_(True))
        .filter(Category.name != "Bebidas")
        .order_by(Product.name)
        .all()
    )

    if request.method == "POST":
        try:
            production_date_str = request.form.get("production_date")
            production_date = (
                datetime.strptime(production_date_str, "%Y-%m-%d").date() if production_date_str else date.today()
            )

            product_ids = request.form.getlist("product_id[]")
            quantities = request.form.getlist("quantity[]")
            items = [
                {"product_id": product_id, "quantity": quantity}
                for product_id, quantity in zip(product_ids, quantities)
                if product_id and quantity
            ]

            if not items:
                raise ValueError("Adicione pelo menos um produto à produção.")

            notes = request.form.get("notes", "").strip() or None
            production = create_production(production_date, items, notes)
            flash(f"Produção de {production.production_date.strftime('%d/%m/%Y')} criada com sucesso.", "success")
            return redirect(url_for("production.index"))
        except (ValueError, KeyError) as exc:
            flash(str(exc), "error")

    return render_template("production/form.html", products=products)


@production_bp.get("/<int:production_id>")
def detail(production_id):
    production = Production.query.get_or_404(production_id)
    return render_template("production/detail.html", production=production)


@production_bp.route("/<int:production_id>/finalizar", methods=["GET", "POST"])
def finalize(production_id):
    production = Production.query.get_or_404(production_id)

    if request.method == "POST":
        try:
            sold_items = {}
            for item in production.items:
                sold_qty = request.form.get(f"sold_{item.id}", "0")
                sold_items[str(item.product_id)] = Decimal(str(int(float(sold_qty)))) if sold_qty and sold_qty != "0" else Decimal("0")

            production, sale = finalize_production(production_id, sold_items)
            flash(f"Produção finalizada! Venda #{sale.id if sale else 'N/A'} registrada.", "success")
            return redirect(url_for("production.index"))
        except (ValueError, KeyError) as exc:
            flash(str(exc), "error")

    return render_template("production/finalize.html", production=production)


@production_bp.route("/<int:production_id>/editar", methods=["GET", "POST"])
def edit(production_id):
    production = Production.query.get_or_404(production_id)

    if production.status == "FINALIZADA":
        flash("Não é possível editar uma produção finalizada.", "error")
        return redirect(url_for("production.detail", production_id=production_id))

    # Filtrar apenas produtos que não são bebidas
    products = (
        Product.query.join(Category)
        .filter(Product.active.is_(True))
        .filter(Category.name != "Bebidas")
        .order_by(Product.name)
        .all()
    )

    if request.method == "POST":
        try:
            production_date_str = request.form.get("production_date")
            production_date = (
                datetime.strptime(production_date_str, "%Y-%m-%d").date() if production_date_str else production.production_date
            )

            product_ids = request.form.getlist("product_id[]")
            quantities = request.form.getlist("quantity[]")
            items = [
                {"product_id": product_id, "quantity": quantity}
                for product_id, quantity in zip(product_ids, quantities)
                if product_id and quantity
            ]

            if not items:
                raise ValueError("Adicione pelo menos um produto à produção.")

            notes = request.form.get("notes", "").strip() or None
            production = update_production(production_id, items, notes)
            flash(f"Produção atualizada com sucesso.", "success")
            return redirect(url_for("production.detail", production_id=production_id))
        except (ValueError, KeyError) as exc:
            flash(str(exc), "error")

    return render_template("production/form.html", production=production, products=products)
