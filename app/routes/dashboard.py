from datetime import datetime, time
from decimal import Decimal

from flask import Blueprint, render_template
from sqlalchemy import func

from app.models import Product, Sale, SaleItem


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/")
def index():
    now = datetime.now()
    day_start = datetime.combine(now.date(), time.min)
    month_start = datetime(now.year, now.month, 1)

    today_sales = Sale.query.filter(Sale.sale_date >= day_start).all()
    month_sales = Sale.query.filter(Sale.sale_date >= month_start).all()

    today_revenue = sum((Decimal(s.total) for s in today_sales), Decimal("0.00"))
    today_cost = sum((s.cost_total for s in today_sales), Decimal("0.00"))
    month_revenue = sum((Decimal(s.total) for s in month_sales), Decimal("0.00"))
    month_cost = sum((s.cost_total for s in month_sales), Decimal("0.00"))

    top_products = (
        SaleItem.query.join(Sale)
        .filter(Sale.sale_date >= month_start)
        .with_entities(SaleItem.product_id, func.sum(SaleItem.quantity).label("quantity"))
        .group_by(SaleItem.product_id)
        .order_by(func.sum(SaleItem.quantity).desc())
        .limit(5)
        .all()
    )

    top_product_rows = []
    for product_id, quantity in top_products:
        product = db_product = Product.query.get(product_id)
        if product:
            top_product_rows.append((product, quantity))

    low_stock = (
        Product.query.filter(Product.active.is_(True))
        .filter(Product.min_stock > 0)
        .filter(Product.stock_quantity <= Product.min_stock)
        .order_by(Product.stock_quantity.asc())
        .limit(8)
        .all()
    )

    low_margin = (
        Product.query.filter(Product.active.is_(True))
        .order_by(Product.sale_price.asc())
        .all()
    )
    low_margin = [p for p in low_margin if p.margin_percent < Decimal("30")] [:8]

    return render_template(
        "dashboard.html",
        today_revenue=today_revenue,
        today_cost=today_cost,
        today_profit=today_revenue - today_cost,
        month_revenue=month_revenue,
        month_cost=month_cost,
        month_profit=month_revenue - month_cost,
        top_products=top_product_rows,
        low_stock=low_stock,
        low_margin=low_margin,
    )
