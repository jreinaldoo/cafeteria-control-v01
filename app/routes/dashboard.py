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
        .all()
    )

    # weekday() retorna 0=Segunda, 1=Terça, ..., 6=Domingo
    days_of_week = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    sales_by_day = {day: 0 for day in days_of_week}

    for sale in sales:
        # Usar a data local da venda (ignorando timezone)
        sale_date = sale.sale_date.date() if hasattr(sale.sale_date, 'date') else sale.sale_date
        day_name = days_of_week[sale_date.weekday()]
        sales_by_day[day_name] += float(sale.total)

    return list(sales_by_day.keys()), list(sales_by_day.values())


def get_monthly_sales():
    """Vendas por dia (último mês)"""
    now = datetime.now()
    month_ago = now - timedelta(days=30)
    day_start = datetime.combine(month_ago.date(), time.min)

    sales = Sale.query.filter(Sale.sale_date >= day_start).all()

    sales_by_date = {}
    for sale in sales:
        sale_date = sale.sale_date.date() if hasattr(sale.sale_date, 'date') else sale.sale_date
        date_str = sale_date.strftime("%d/%m")
        sales_by_date[date_str] = sales_by_date.get(date_str, 0) + float(sale.total)

    labels = []
    values = []
    for date_str in sorted(sales_by_date.keys()):
        labels.append(date_str)
        values.append(sales_by_date[date_str])

    return labels, values


def get_6month_sales():
    """Vendas por mês (últimos 6 meses)"""
    now = datetime.now()
    six_months_ago = now - timedelta(days=180)
    day_start = datetime.combine(six_months_ago.date(), time.min)

    sales = Sale.query.filter(Sale.sale_date >= day_start).all()

    months_pt = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    sales_by_month = {}

    for sale in sales:
        sale_date = sale.sale_date.date() if hasattr(sale.sale_date, 'date') else sale.sale_date
        year = sale_date.year
        month = sale_date.month
        label = f"{months_pt[month - 1]}/{str(year)[-2:]}"
        sales_by_month[label] = sales_by_month.get(label, 0) + float(sale.total)

    labels = []
    values = []
    for label in sorted(sales_by_month.keys()):
        labels.append(label)
        values.append(sales_by_month[label])

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
