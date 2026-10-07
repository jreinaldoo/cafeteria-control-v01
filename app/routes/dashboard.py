from datetime import datetime, timedelta, time
from decimal import Decimal

from flask import Blueprint, render_template
from sqlalchemy import func

from app import db
from app.models import Product, Sale, SaleItem, Purchase, Production, ProductionItem


dashboard_bp = Blueprint("dashboard", __name__)


def get_weekly_sales():
    """Vendas por dia da semana (semana atual: segunda a domingo) separadas por tipo de pagamento"""
    now = datetime.now()
    # Encontrar segunda-feira da semana atual
    weekday = now.weekday()  # 0=Segunda, 6=Domingo
    week_start = now - timedelta(days=weekday)
    day_start = datetime.combine(week_start.date(), time.min)
    # Domingo às 23:59:59
    week_end = day_start + timedelta(days=6, hours=23, minutes=59, seconds=59)

    sales = (
        Sale.query.filter(Sale.sale_date >= day_start, Sale.sale_date <= week_end)
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

    total = sum(pix_by_day.values()) + sum(sumup_by_day.values())
    return list(pix_by_day.keys()), list(pix_by_day.values()), list(sumup_by_day.values()), total


def get_monthly_sales():
    """Vendas por dia (último mês) separadas por tipo de pagamento"""
    now = datetime.now()
    month_ago = now - timedelta(days=30)

    # Gerar todos os dias dos últimos 30 dias sequencialmente
    labels = []
    for i in range(29, -1, -1):
        day_date = now - timedelta(days=i)
        labels.append(day_date.strftime("%d/%m"))

    # Buscar vendas e agrupar por data
    day_start = datetime.combine(month_ago.date(), time.min)
    sales = Sale.query.filter(Sale.sale_date >= day_start).all()

    pix_by_date = {}
    sumup_by_date = {}

    for sale in sales:
        sale_date = sale.sale_date.date() if hasattr(sale.sale_date, 'date') else sale.sale_date
        if sale.payment_method == "PIX":
            pix_by_date[sale_date] = pix_by_date.get(sale_date, 0) + float(sale.total)
        elif sale.payment_method == "SUMUP":
            sumup_by_date[sale_date] = sumup_by_date.get(sale_date, 0) + float(sale.total)

    # Preencher valores para cada dia
    pix_values = []
    sumup_values = []
    for i in range(29, -1, -1):
        day_date = now - timedelta(days=i)
        day_start_date = datetime.combine(day_date.date(), time.min)
        day_end_date = datetime.combine(day_date.date(), time.max)

        day_pix = 0
        day_sumup = 0
        for sale_date, total in pix_by_date.items():
            sale_dt = sale_date if isinstance(sale_date, datetime) else datetime.combine(sale_date, time.min)
            if day_start_date <= sale_dt <= day_end_date:
                day_pix += total
        for sale_date, total in sumup_by_date.items():
            sale_dt = sale_date if isinstance(sale_date, datetime) else datetime.combine(sale_date, time.min)
            if day_start_date <= sale_dt <= day_end_date:
                day_sumup += total

        pix_values.append(day_pix)
        sumup_values.append(day_sumup)

    total = sum(pix_values) + sum(sumup_values)
    return labels, pix_values, sumup_values, total


def get_6month_sales():
    """Vendas por mês (últimos 6 meses) separadas por tipo de pagamento"""
    now = datetime.now()
    months_pt = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

    # Gerar os últimos 6 meses sequencialmente
    labels = []
    for i in range(5, -1, -1):
        month_date = now - timedelta(days=30 * i)
        year = month_date.year
        month = month_date.month
        label = f"{months_pt[month - 1]}/{str(year)[-2:]}"
        labels.append(label)

    # Buscar vendas e agrupar por mês
    six_months_ago = now - timedelta(days=180)
    day_start = datetime.combine(six_months_ago.date(), time.min)
    sales = Sale.query.filter(Sale.sale_date >= day_start).all()

    pix_by_month = {}
    sumup_by_month = {}

    for sale in sales:
        sale_date = sale.sale_date.date() if hasattr(sale.sale_date, 'date') else sale.sale_date
        if sale.payment_method == "PIX":
            pix_by_month[sale_date] = pix_by_month.get(sale_date, 0) + float(sale.total)
        elif sale.payment_method == "SUMUP":
            sumup_by_month[sale_date] = sumup_by_month.get(sale_date, 0) + float(sale.total)

    # Preencher valores para cada mês
    pix_values = []
    sumup_values = []
    for i in range(5, -1, -1):
        month_date = now - timedelta(days=30 * i)
        month_start = datetime(month_date.year, month_date.month, 1)
        month_end = datetime(month_date.year, month_date.month, 1) + timedelta(days=32)
        month_end = month_end.replace(day=1) - timedelta(days=1)

        month_pix = 0
        month_sumup = 0
        for sale_date, total in pix_by_month.items():
            sale_dt = sale_date if isinstance(sale_date, datetime) else datetime.combine(sale_date, time.min)
            if month_start <= sale_dt <= month_end:
                month_pix += total
        for sale_date, total in sumup_by_month.items():
            sale_dt = sale_date if isinstance(sale_date, datetime) else datetime.combine(sale_date, time.min)
            if month_start <= sale_dt <= month_end:
                month_sumup += total

        pix_values.append(month_pix)
        sumup_values.append(month_sumup)

    total = sum(pix_values) + sum(sumup_values)
    return labels, pix_values, sumup_values, total


def get_monthly_purchases():
    """Compras por dia (último mês)"""
    now = datetime.now()
    month_ago = now - timedelta(days=30)

    # Gerar todos os dias dos últimos 30 dias sequencialmente
    labels = []
    values = []
    for i in range(29, -1, -1):
        day_date = now - timedelta(days=i)
        labels.append(day_date.strftime("%d/%m"))
        values.append(0)

    # Buscar compras e agrupar por data
    day_start = datetime.combine(month_ago.date(), time.min)
    purchases = Purchase.query.filter(Purchase.purchase_date >= day_start).all()

    purchases_by_date = {}
    for purchase in purchases:
        purchase_date = purchase.purchase_date if hasattr(purchase.purchase_date, 'strftime') else purchase.purchase_date
        purchases_by_date[purchase_date] = purchases_by_date.get(purchase_date, 0) + float(purchase.total)

    # Preencher valores para cada dia
    for i in range(29, -1, -1):
        day_date = now - timedelta(days=i)
        day_start_date = datetime.combine(day_date.date(), time.min)
        day_end_date = datetime.combine(day_date.date(), time.max)

        day_total = 0
        for purchase_date, total in purchases_by_date.items():
            purchase_dt = purchase_date if isinstance(purchase_date, datetime) else datetime.combine(purchase_date, time.min)
            if day_start_date <= purchase_dt <= day_end_date:
                day_total += total

        values[29 - i] = day_total

    total = sum(values, 0)
    return labels, values, total


def get_6month_purchases():
    """Compras por mês (últimos 6 meses)"""
    now = datetime.now()
    months_pt = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

    # Gerar os últimos 6 meses sequencialmente
    labels = []
    values = []
    for i in range(5, -1, -1):
        month_date = now - timedelta(days=30 * i)
        year = month_date.year
        month = month_date.month
        label = f"{months_pt[month - 1]}/{str(year)[-2:]}"
        labels.append(label)

    # Buscar compras e agrupar por mês
    six_months_ago = now - timedelta(days=180)
    day_start = datetime.combine(six_months_ago.date(), time.min)
    purchases = Purchase.query.filter(Purchase.purchase_date >= day_start).all()

    purchases_by_month = {}
    for purchase in purchases:
        purchase_date = purchase.purchase_date if hasattr(purchase.purchase_date, 'year') else purchase.purchase_date
        purchases_by_month[purchase_date] = purchases_by_month.get(purchase_date, 0) + float(purchase.total)

    # Preencher valores para cada mês
    for i in range(5, -1, -1):
        month_date = now - timedelta(days=30 * i)
        month_start = datetime(month_date.year, month_date.month, 1)
        month_end = datetime(month_date.year, month_date.month, 1) + timedelta(days=32)
        month_end = month_end.replace(day=1) - timedelta(days=1)

        month_total = 0
        for purchase_date, total in purchases_by_month.items():
            purchase_dt = purchase_date if isinstance(purchase_date, datetime) else datetime.combine(purchase_date, time.min)
            if month_start <= purchase_dt <= month_end:
                month_total += total

        values.append(month_total)

    total = sum(values, 0)
    return labels, values, total


def get_daily_losses():
    """Perdas diárias (últimos 30 dias) com quantidade e custo"""
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)
    day_start = datetime.combine(thirty_days_ago.date(), time.min)

    # Buscar produções finalizadas
    productions = Production.query.filter(
        Production.status == "FINALIZADA",
        Production.finalized_at >= day_start
    ).all()

    # Agrupar perdas por data
    losses_by_date = {}
    for production in productions:
        prod_date = production.production_date
        prod_dt = prod_date if isinstance(prod_date, datetime) else datetime.combine(prod_date, time.min)

        for item in production.items:
            if item.quantity_lost > 0:
                if prod_dt not in losses_by_date:
                    losses_by_date[prod_dt] = {"quantity": 0, "cost": 0}
                losses_by_date[prod_dt]["quantity"] += item.quantity_lost
                # Calcular custo: quantidade perdida * custo do produto
                losses_by_date[prod_dt]["cost"] += item.quantity_lost * item.product.cost

    # Gerar labels dos últimos 30 dias
    labels = []
    quantities = []
    costs = []
    for i in range(29, -1, -1):
        day_date = now - timedelta(days=i)
        labels.append(day_date.strftime("%d/%m"))

        day_dt = datetime.combine(day_date.date(), time.min)
        day_end_dt = datetime.combine(day_date.date(), time.max)

        if day_dt in losses_by_date:
            quantities.append(float(losses_by_date[day_dt]["quantity"]))
            costs.append(float(losses_by_date[day_dt]["cost"]))
        else:
            quantities.append(0)
            costs.append(0)

    total_quantity = sum(quantities, 0)
    total_cost = sum(costs, 0)
    return labels, quantities, costs, total_quantity, total_cost


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

    # Calcular margem percentual
    today_margin = Decimal("0")
    if today_revenue > 0:
        today_margin = ((today_revenue - today_cost) / today_revenue) * Decimal("100")

    month_margin = Decimal("0")
    if month_revenue > 0:
        month_margin = ((month_revenue - month_cost) / month_revenue) * Decimal("100")

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
    weekly_labels, weekly_pix, weekly_sumup, weekly_total = get_weekly_sales()
    monthly_labels, monthly_pix, monthly_sumup, monthly_total = get_monthly_sales()
    six_month_labels, six_month_pix, six_month_sumup, six_month_total = get_6month_sales()

    # Dados para gráficos de compras
    monthly_purchase_labels, monthly_purchase_values, monthly_purchase_total = get_monthly_purchases()
    six_month_purchase_labels, six_month_purchase_values, six_month_purchase_total = get_6month_purchases()

    # Dados para gráfico de perdas
    loss_labels, loss_quantities, loss_costs, loss_total_quantity, loss_total_cost = get_daily_losses()

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
        top_products=top_product_rows,
        low_stock=low_stock,
        low_margin=low_margin,
        weekly_labels=weekly_labels,
        weekly_pix=weekly_pix,
        weekly_sumup=weekly_sumup,
        weekly_total=weekly_total,
        monthly_labels=monthly_labels,
        monthly_pix=monthly_pix,
        monthly_sumup=monthly_sumup,
        monthly_total=monthly_total,
        six_month_labels=six_month_labels,
        six_month_pix=six_month_pix,
        six_month_sumup=six_month_sumup,
        six_month_total=six_month_total,
        monthly_purchase_labels=monthly_purchase_labels,
        monthly_purchase_values=monthly_purchase_values,
        monthly_purchase_total=monthly_purchase_total,
        six_month_purchase_labels=six_month_purchase_labels,
        six_month_purchase_values=six_month_purchase_values,
        six_month_purchase_total=six_month_purchase_total,
        loss_labels=loss_labels,
        loss_quantities=loss_quantities,
        loss_costs=loss_costs,
        loss_total_quantity=loss_total_quantity,
        loss_total_cost=loss_total_cost,
    )
