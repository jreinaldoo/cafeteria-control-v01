from datetime import datetime, timedelta, time
from decimal import Decimal

from flask import Blueprint, render_template
from sqlalchemy import func

from app import db
from app.models import Product, Sale, SaleItem


dashboard_bp = Blueprint("dashboard", __name__)


def get_weekly_sales():
    """Vendas por dia da semana (últimos 7 dias)"""
    now = datetime.now()
    week_ago = now - timedelta(days=6)
    day_start = datetime.combine(week_ago.date(), time.min)

    sales = (
        Sale.query.filter(Sale.sale_date >= day_start)
        .with_entities(
            func.date(Sale.sale_date).label("date"),
            func.sum(Sale.total).label("total"),
        )
        .group_by(func.date(Sale.sale_date))
        .order_by(func.date(Sale.sale_date))
        .all()
    )

    days_of_week = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
    sales_by_day = {day: 0 for day in days_of_week}

    for date_str, total in sales:
        if isinstance(date_str, str):
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            date_obj = date_str
        day_name = days_of_week[date_obj.weekday()]
        sales_by_day[day_name] = float(total)

    return list(sales_by_day.keys()), list(sales_by_day.values())


def get_monthly_sales():
    """Vendas por dia (último mês)"""
    now = datetime.now()
    month_ago = now - timedelta(days=30)
    day_start = datetime.combine(month_ago.date(), time.min)

    sales = (
        Sale.query.filter(Sale.sale_date >= day_start)
        .with_entities(
            func.date(Sale.sale_date).label("date"),
            func.sum(Sale.total).label("total"),
        )
        .group_by(func.date(Sale.sale_date))
        .order_by(func.date(Sale.sale_date))
        .all()
    )

    labels = []
    values = []
    for date_str, total in sales:
        if isinstance(date_str, str):
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            date_obj = date_str
        labels.append(date_obj.strftime("%d/%m"))
        values.append(float(total))

    return labels, values


def get_6month_sales():
    """Vendas por mês (últimos 6 meses)"""
    now = datetime.now()
    six_months_ago = now - timedelta(days=180)
    day_start = datetime.combine(six_months_ago.date(), time.min)

    sales = (
        Sale.query.filter(Sale.sale_date >= day_start)
        .with_entities(
            func.strftime("%Y-%m", Sale.sale_date).label("month"),
            func.sum(Sale.total).label("total"),
        )
        .group_by(func.strftime("%Y-%m", Sale.sale_date))
        .order_by(func.strftime("%Y-%m", Sale.sale_date))
        .all()
    )

    months_pt = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    labels = []
    values = []

    for month_str, total in sales:
        if isinstance(month_str, str):
            year, month = map(int, month_str.split("-"))
        else:
            year = month_str.year
            month = month_str.month
        label = f"{months_pt[month - 1]}/{str(year)[-2:]}"
        labels.append(label)
        values.append(float(total))

    return labels, values


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

    # Dados para gráficos
    weekly_labels, weekly_values = get_weekly_sales()
    monthly_labels, monthly_values = get_monthly_sales()
    six_month_labels, six_month_values = get_6month_sales()

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
        weekly_labels=weekly_labels,
        weekly_values=weekly_values,
        monthly_labels=monthly_labels,
        monthly_values=monthly_values,
        six_month_labels=six_month_labels,
        six_month_values=six_month_values,
    )
