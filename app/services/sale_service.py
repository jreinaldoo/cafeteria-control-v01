from datetime import datetime
from decimal import Decimal

from app import db
from app.models import Product, Sale, SaleItem
from app.services.stock_service import move_stock


VALID_PAYMENT_METHODS = {"PIX", "SUMUP"}


def create_sale(items, payment_method, sale_date=None, description=None, is_generic=False, total=None):
    if payment_method not in VALID_PAYMENT_METHODS:
        raise ValueError("Forma de pagamento inválida.")

    if is_generic:
        if not total or total <= 0:
            raise ValueError("Informe o valor total da venda.")
        if not description:
            raise ValueError("Informe uma descrição para a venda.")
    else:
        if not items:
            raise ValueError("A venda precisa ter pelo menos um produto.")

    try:
        sale = Sale(
            payment_method=payment_method,
            sale_date=sale_date or datetime.utcnow(),
            description=description,
            is_generic=is_generic,
            total=Decimal(str(total)) if total else Decimal("0.00")
        )
        db.session.add(sale)
        db.session.flush()

        if not is_generic:
            total = Decimal("0.00")
            for item in items:
                product = db.session.get(Product, int(item["product_id"]))
                quantity = Decimal(str(item["quantity"]))
                if not product or not product.active:
                    raise ValueError("Produto inválido ou inativo.")
                if quantity <= 0:
                    raise ValueError("A quantidade deve ser maior que zero.")
                if Decimal(product.stock_quantity or 0) < quantity:
                    raise ValueError(f"Estoque insuficiente para {product.name}.")

                unit_price = Decimal(product.sale_price)
                unit_cost = Decimal(product.cost)
                subtotal = (unit_price * quantity).quantize(Decimal("0.01"))
                total += subtotal

                sale.items.append(
                    SaleItem(
                        product=product,
                        quantity=quantity,
                        unit_price=unit_price,
                        unit_cost=unit_cost,
                        subtotal=subtotal,
                    )
                )
                move_stock(product, -quantity, "VENDA", "SALE", sale.id)

            sale.total = total

        db.session.commit()
        return sale
    except Exception:
        db.session.rollback()
        raise


def update_sale(sale_id, items, payment_method, sale_date=None):
    if payment_method not in VALID_PAYMENT_METHODS:
        raise ValueError("Forma de pagamento inválida.")
    if not items:
        raise ValueError("A venda precisa ter pelo menos um produto.")

    try:
        sale = db.session.get(Sale, sale_id)
        if not sale:
            raise ValueError("Venda não encontrada.")
        if sale.is_generic:
            raise ValueError("Não é possível editar vendas genéricas.")

        # Reverter movimentações de estoque originais
        for item in sale.items:
            product = db.session.get(Product, item.product_id)
            if product:
                move_stock(product, item.quantity, "ESTORNO VENDA", "SALE", sale.id)

        # Remover todos os itens existentes
        for item in sale.items:
            db.session.delete(item)

        total = Decimal("0.00")
        for item in items:
            product = db.session.get(Product, int(item["product_id"]))
            quantity = Decimal(str(item["quantity"]))
            if not product or not product.active:
                raise ValueError("Produto inválido ou inativo.")
            if quantity <= 0:
                raise ValueError("A quantidade deve ser maior que zero.")
            if Decimal(product.stock_quantity or 0) < quantity:
                raise ValueError(f"Estoque insuficiente para {product.name}.")

            unit_price = Decimal(product.sale_price)
            unit_cost = Decimal(product.cost)
            subtotal = (unit_price * quantity).quantize(Decimal("0.01"))
            total += subtotal

            sale.items.append(
                SaleItem(
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    unit_cost=unit_cost,
                    subtotal=subtotal,
                )
            )
            move_stock(product, -quantity, "VENDA", "SALE", sale.id)

        sale.payment_method = payment_method
        sale.total = total
        if sale_date:
            sale.sale_date = sale_date
        db.session.commit()
        return sale
    except Exception:
        db.session.rollback()
        raise
