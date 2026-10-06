from datetime import datetime, date
from decimal import Decimal

from app import db
from app.models import Product, Production, ProductionItem, Sale, SaleItem
from app.services.sale_service import create_sale
from app.services.stock_service import move_stock


def create_production(production_date, items, notes=None):
    """Cria uma nova produção"""
    try:
        production = Production(production_date=production_date, notes=notes)
        db.session.add(production)
        db.session.flush()

        for item in items:
            product = db.session.get(Product, int(item["product_id"]))
            quantity = Decimal(str(item["quantity"]))
            if not product or not product.active:
                raise ValueError("Produto inválido ou inativo.")
            if quantity <= 0:
                raise ValueError("A quantidade deve ser maior que zero.")

            production.items.append(
                ProductionItem(
                    product=product,
                    quantity_produced=quantity,
                    quantity_sold=Decimal("0"),
                    quantity_lost=Decimal("0"),
                )
            )

        db.session.commit()
        return production
    except Exception:
        db.session.rollback()
        raise


def finalize_production(production_id, sold_items):
    """Finaliza a produção: cria venda do vendido e registra perdas"""
    try:
        production = db.session.get(Production, production_id)
        if not production:
            raise ValueError("Produção não encontrada.")
        if production.status == "FINALIZADA":
            raise ValueError("Esta produção já foi finalizada.")

        # Atualizar quantidades vendidas e calcular perdas
        for item in production.items:
            product_id = item.product_id
            sold_quantity = Decimal(str(sold_items.get(str(product_id), 0)))
            item.quantity_sold = sold_quantity
            item.quantity_lost = item.quantity_produced - sold_quantity

        # Criar venda apenas dos itens vendidos
        sale_items_to_create = []
        for item in production.items:
            if item.quantity_sold > 0:
                sale_items_to_create.append({
                    "product_id": item.product_id,
                    "quantity": item.quantity_sold
                })

        if sale_items_to_create:
            # Criar venda com PIX como padrão (pode ser ajustado depois)
            sale = create_sale(sale_items_to_create, "PIX", datetime.combine(production.production_date, datetime.min.time()))
        else:
            sale = None

        # Atualizar status da produção
        production.status = "FINALIZADA"
        production.finalized_at = datetime.utcnow()

        db.session.commit()
        return production, sale
    except Exception:
        db.session.rollback()
        raise


def get_production_by_date(production_date):
    """Busca produção por data"""
    return Production.query.filter_by(production_date=production_date).first()


def get_open_production():
    """Busca produção aberta mais recente"""
    return Production.query.filter_by(status="ABERTA").order_by(Production.production_date.desc()).first()
