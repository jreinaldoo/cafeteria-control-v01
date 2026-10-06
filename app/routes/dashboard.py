from datetime import datetime, timedelta, time
from decimal import Decimal

from flask import Blueprint, render_template
from sqlalchemy import func

from app import db
from app.models import Product, Sale, SaleItem


dashboard_bp = Blueprint("dashboard", __name__)


def get_weekly_sales():
    """Vendas por dia da semana (últimos 7 dias) separadas por tipo de pagamento"""
    now = datetime.now()
    week_ago = now - timedelta(days=6)
    day_start = datetime.combine(week_ago.date(), time.min)

    sales = (
        Sale.query.filter(Sale.sale_date >= day_start)
        .all()
    )

    # weekday() retorna 0=Segunda, 1=Terça, ..., 6=Domingo
    days_of_week = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    pix_by_day = {day: 0 for day in days_of_week}
    sumup_by_day = {day: 0 for day in days_of_week}

    for sale in sales:
        # Usar a data local da venda (ignorando timezone)
        sale_date = sale.sale_date.date() if hasattr(sale.sale_date, 'date') else sale.sale_date
        day_name = days_of_week[sale_date.weekday()]
        if sale.payment_method == "PIX":
            pix_by_day[day_name] += float(sale.total)
        elif sale.payment_method == "SUMUP":
            sumup_by_day[day_name] += float(sale.total)

    return list(pix_by_day.keys()), list(pix_by_day.values()), list(sumup_by_day.values())


def get_monthly_sales():
    """Vendas por dia (último mês) separadas por tipo de pagamento"""
    now = datetime.now()
    month_ago = now - timedelta(days=30)
    day_start = datetime.combine(month_ago.date(), time.min)

    sales = Sale.query.filter(Sale.sale_date >= day_start).all()

    pix_by_date = {}
    sumup_by_date = {}

    for sale in sales:
        sale_date = sale.sale_date.date() if hasattr(sale.sale_date, 'date') else sale.sale_date
        date_str = sale_date.strftime("%d/%m")
        if sale.payment_method == "PIX":
            pix_by_date[date_str] = pix_by_date.get(date_str, 0) + float(sale.total)
        elif sale.payment_method == "SUMUP":
            sumup_by_date[date_str] = sumup_by_date.get(date_str, 0) + float(sale.total)

    labels = []
    pix_values = []
    sumup_values = []

    all_dates = sorted(set(list(pix_by_date.keys()) + list(sumup_by_date.keys())))
    for date_str in all_dates:
        labels.append(date_str)
        pix_values.append(pix_by_date.get(date_str, 0))
        sumup_values.append(sumup_by_date.get(date_str, 0))

    return labels, pix_values, sumup_values


def get_6month_sales():
    """Vendas por mês (últimos 6 meses) separadas por tipo de pagamento"""
    now = datetime.now()
    six_months_ago = now - timedelta(days=180)
    day_start = datetime.combine(six_months_ago.date(), time.min)

    sales = Sale.query.filter(Sale.sale_date >= day_start).all()

    months_pt = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    pix_by_month = {}
    sumup_by_month = {}

    for sale in sales:
        sale_date = sale.sale_date.date() if hasattr(sale.sale_date, 'date') else sale.sale_date
        year = sale_date.year
        month = sale_date.month
        label = f"{months_pt[month - 1]}/{str(year)[-2:]}"
        if sale.payment_method == "PIX":
            pix_by_month[label] = pix_by_month.get(label, 0) + float(sale.total)
        elif sale.payment_method == "SUMUP":
            sumup_by_month[label] = sumup_by_month.get(label, 0) + float(sale.total)

    labels = []
    pix_values = []
    sumup_values = []

    all_months = sorted(set(list(pix_by_month.keys()) + list(sumup_by_month.keys())))
    for label in all_months:
        labels.append(label)
        pix_values.append(pix_by_month.get(label, 0))
        sumup_values.append(sumup_by_month.get(label, 0))

    return labels, pix_values, sumup_values


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
    weekly_labels, weekly_pix, weekly_sumup = get_weekly_sales()
    monthly_labels, monthly_pix, monthly_sumup = get_monthly_sales()
    six_month_labels, six_month_pix, six_month_sumup = get_6month_sales()

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
        weekly_pix=weekly_pix,
        weekly_sumup=weekly_sumup,
        monthly_labels=monthly_labels,
        monthly_pix=monthly_pix,
        monthly_sumup=monthly_sumup,
        six_month_labels=six_month_labels,
        six_month_pix=six_month_pix,
        six_month_sumup=six_month_sumup,
    )
