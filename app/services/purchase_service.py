from datetime import date
from decimal import Decimal

from app import db
from app.models import Product, Purchase, PurchaseItem
from app.services.stock_service import move_stock


def create_purchase(product_id, quantity, unit_cost, supplier=None, purchase_date=None):
    try:
        product = db.session.get(Product, int(product_id))
        quantity = Decimal(str(int(quantity)))
        unit_cost = Decimal(str(unit_cost))

        if not product:
            raise ValueError("Produto não encontrado.")
        if quantity <= 0 or unit_cost < 0:
            raise ValueError("Quantidade e custo precisam ser válidos.")

        old_qty = Decimal(product.stock_quantity or 0)
        old_cost = Decimal(product.cost or 0)
        total = (quantity * unit_cost).quantize(Decimal("0.01"))

        purchase = Purchase(supplier=supplier, total=total, purchase_date=purchase_date or date.today())
        db.session.add(purchase)
        db.session.flush()
        purchase.items.append(
            PurchaseItem(
                product=product,
                quantity=quantity,
                unit_cost=unit_cost,
                total=total,
            )
        )

        # Custo médio ponderado, usando o estoque existente como base.
        new_qty = old_qty + quantity
        if new_qty > 0:
            product.cost = ((old_qty * old_cost) + (quantity * unit_cost)) / new_qty

        move_stock(product, quantity, "COMPRA", "PURCHASE", purchase.id)
        db.session.commit()
        return purchase
    except Exception:
        db.session.rollback()
        raise


def update_purchase(purchase_id, product_id, quantity, unit_cost, supplier=None, purchase_date=None):
    try:
        purchase = db.session.get(Purchase, purchase_id)
        if not purchase:
            raise ValueError("Compra não encontrada.")

        product = db.session.get(Product, int(product_id))
        quantity = Decimal(str(int(quantity)))
        unit_cost = Decimal(str(unit_cost))

        if not product:
            raise ValueError("Produto não encontrado.")
        if quantity <= 0 or unit_cost < 0:
            raise ValueError("Quantidade e custo precisam ser válidos.")

        # Reverter movimentação de estoque original
        old_item = purchase.items[0] if purchase.items else None
        if old_item:
            old_product = db.session.get(Product, old_item.product_id)
            if old_product:
                move_stock(old_product, -old_item.quantity, "ESTORNO COMPRA", "PURCHASE", purchase.id)

        # Remover item antigo
        for item in purchase.items:
            db.session.delete(item)

        # Calcular novo custo médio ponderado
        old_qty = Decimal(product.stock_quantity or 0)
        old_cost = Decimal(product.cost or 0)
        total = (quantity * unit_cost).quantize(Decimal("0.01"))

        # Adicionar novo item
        purchase.items.append(
            PurchaseItem(
                product=product,
                quantity=quantity,
                unit_cost=unit_cost,
                total=total,
            )
        )

        # Custo médio ponderado
        new_qty = old_qty + quantity
        if new_qty > 0:
            product.cost = ((old_qty * old_cost) + (quantity * unit_cost)) / new_qty

        move_stock(product, quantity, "COMPRA", "PURCHASE", purchase.id)
        purchase.supplier = supplier
        purchase.total = total
        if purchase_date:
            purchase.purchase_date = purchase_date
        db.session.commit()
        return purchase
    except Exception:
        db.session.rollback()
        raise
