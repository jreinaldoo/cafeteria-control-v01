from datetime import datetime, time
from decimal import Decimal

from flask import Blueprint, render_template

from app import db
from app.models import Sale
from app.services.production_service import get_open_production


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

    today_margin = Decimal("0")
    if today_revenue > 0:
        today_margin = ((today_revenue - today_cost) / today_revenue) * Decimal("100")

    month_margin = Decimal("0")
    if month_revenue > 0:
        month_margin = ((month_revenue - month_cost) / month_revenue) * Decimal("100")

    open_production = get_open_production()

    return render_template(
        "dashboard.html",
        today_revenue=today_revenue,
        today_cost=today_cost,
        today_profit=today_revenue - today_cost,
        today_margin=today_margin,
        month_revenue=month_revenue,
        month_cost=month_cost,
        month_profit=month_revenue - month_cost,
        month_margin=month_margin,
        open_production=open_production,
    )
