from decimal import Decimal

from app import db
from app.models import Category, Product


INITIAL_PRODUCTS = [
    ("Salgados", "Pão de Queijo", "1.50", "5.00"),
    ("Salgados", "Esfiha de Carne", "4.80", "8.00"),
    ("Salgados", "Croissant de Frango com Requeijão", "4.80", "8.00"),
    ("Doces", "Cookie Tradicional", "7.70", "10.00"),
    ("Doces", "Cookie Nutella", "10.80", "15.00"),
    ("Bebidas", "Coca-Cola Lata 220ml", "2.40", "3.00"),
    ("Bebidas", "Guaraná Kuat 200ml", "1.80", "2.50"),
    ("Bebidas", "Fanta 200ml", "1.80", "2.50"),
    ("Bebidas", "Suco Kappo Del Valle Morango/Uva", "2.20", "3.50"),
]


def seed_initial_data():
    if Product.query.count() > 0:
        return

    categories = {}
    for category_name, _, _, _ in INITIAL_PRODUCTS:
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            category = Category(name=category_name)
            db.session.add(category)
        categories[category_name] = category

    # Criar categoria para vendas avulsas
    if "Outros" not in categories:
        outros_category = Category(name="Outros")
        db.session.add(outros_category)
        db.session.flush()
        categories["Outros"] = outros_category

    db.session.flush()

    for category_name, name, cost, price in INITIAL_PRODUCTS:
        db.session.add(
            Product(
                category=categories[category_name],
                name=name,
                cost=Decimal(cost),
                sale_price=Decimal(price),
                stock_quantity=Decimal("0"),
                min_stock=Decimal("0"),
            )
        )

    # Criar produto genérico para vendas avulsas
    db.session.add(
        Product(
            category=categories["Outros"],
            name="Venda avulsa",
            cost=Decimal("0.00"),
            sale_price=Decimal("0.00"),
            stock_quantity=Decimal("999999"),
            min_stock=Decimal("0"),
        )
    )

    db.session.commit()
