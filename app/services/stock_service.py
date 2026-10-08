from decimal import Decimal

from app import db
from app.models import Product, StockMovement


def move_stock(product, quantity, movement_type, reference_type=None, reference_id=None, notes=None):
    quantity = Decimal(str(quantity))
    product.stock_quantity = Decimal(product.stock_quantity or 0) + quantity
    if product.stock_quantity < 0:
        raise ValueError(f"Estoque insuficiente para {product.name}.")

    movement = StockMovement(
        product=product,
        movement_type=movement_type,
        quantity=quantity,
        reference_type=reference_type,
        reference_id=reference_id,
        notes=notes,
    )
    db.session.add(movement)
    return movement


def adjust_stock(product_id, quantity, notes=None):
    product = db.session.get(Product, product_id)
    if not product:
        raise ValueError("Produto não encontrado.")
    quantity = Decimal(str(int(float(quantity))))
    move_stock(product, quantity, "AJUSTE", notes=notes)
    db.session.commit()
    return product
