from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app import db
from app.models import Category, Product

products_bp = Blueprint("products", __name__)


@products_bp.get("/")
def index():
    products = Product.query.order_by(Product.active.desc(), Product.name.asc()).all()
    return render_template("products/index.html", products=products)


@products_bp.route("/novo", methods=["GET", "POST"])
def new():
    categories = Category.query.filter_by(active=True).order_by(Category.name).all()
    if request.method == "POST":
        try:
            name = request.form["name"].strip()
            category_id = int(request.form["category_id"])
            cost = Decimal(request.form["cost"].replace(",", "."))
            sale_price = Decimal(request.form["sale_price"].replace(",", "."))
            min_stock = Decimal(request.form.get("min_stock", "0").replace(",", "."))
            if not name or cost < 0 or sale_price < 0 or min_stock < 0:
                raise ValueError
            if Product.query.filter_by(name=name).first():
                flash("Já existe um produto com esse nome.", "error")
                return render_template("products/form.html", product=None, categories=categories)
            product = Product(
                name=name,
                category_id=category_id,
                cost=cost,
                sale_price=sale_price,
                min_stock=min_stock,
            )
            db.session.add(product)
            db.session.commit()
            flash("Produto cadastrado com sucesso.", "success")
            return redirect(url_for("products.index"))
        except (ValueError, InvalidOperation):
            flash("Confira os valores informados.", "error")
    return render_template("products/form.html", product=None, categories=categories)


@products_bp.route("/<int:product_id>/editar", methods=["GET", "POST"])
def edit(product_id):
    product = db.get_or_404(Product, product_id)
    categories = Category.query.filter_by(active=True).order_by(Category.name).all()
    if request.method == "POST":
        try:
            name = request.form["name"].strip()
            product.name = name
            product.category_id = int(request.form["category_id"])
            product.cost = Decimal(request.form["cost"].replace(",", "."))
            product.sale_price = Decimal(request.form["sale_price"].replace(",", "."))
            product.min_stock = Decimal(request.form.get("min_stock", "0").replace(",", "."))
            product.active = "active" in request.form
            db.session.commit()
            flash("Produto atualizado.", "success")
            return redirect(url_for("products.index"))
        except (ValueError, InvalidOperation):
            db.session.rollback()
            flash("Confira os valores informados.", "error")
    return render_template("products/form.html", product=product, categories=categories)
