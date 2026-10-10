from decimal import Decimal

from app import db
from app.models import Recipe, RecipeItem, Product


def create_recipe(name, description=None):
    """Cria uma nova receita"""
    recipe = Recipe(name=name, description=description)
    db.session.add(recipe)
    db.session.commit()
    return recipe


def add_recipe_item(recipe_id, product_id, quantity_used):
    """Adiciona um item à receita"""
    # Converter quantidade para Decimal
    quantity_used = Decimal(str(float(quantity_used)))

    # Verificar se o produto existe
    product = db.session.get(Product, product_id)
    if not product:
        raise ValueError("Produto não encontrado")

    # Criar o item da receita
    item = RecipeItem(
        recipe_id=recipe_id,
        product_id=product_id,
        quantity_used=quantity_used
    )
    db.session.add(item)
    db.session.commit()
    return item


def update_recipe_item(item_id, product_id, quantity_used):
    """Atualiza um item da receita"""
    item = db.session.get(RecipeItem, item_id)
    if not item:
        raise ValueError("Item não encontrado")

    # Converter quantidade para Decimal
    quantity_used = Decimal(str(float(quantity_used)))

    item.product_id = product_id
    item.quantity_used = quantity_used
    db.session.commit()
    return item


def delete_recipe_item(item_id):
    """Remove um item da receita"""
    item = db.session.get(RecipeItem, item_id)
    if not item:
        raise ValueError("Item não encontrado")

    db.session.delete(item)
    db.session.commit()


def update_recipe(recipe_id, name, description=None):
    """Atualiza dados da receita"""
    recipe = db.session.get(Recipe, recipe_id)
    if not recipe:
        raise ValueError("Receita não encontrada")

    recipe.name = name
    if description is not None:
        recipe.description = description
    db.session.commit()
    return recipe


def delete_recipe(recipe_id):
    """Remove uma receita (e todos os itens via cascade)"""
    recipe = db.session.get(Recipe, recipe_id)
    if not recipe:
        raise ValueError("Receita não encontrada")

    db.session.delete(recipe)
    db.session.commit()


def get_all_recipes():
    """Retorna todas as receitas"""
    return Recipe.query.order_by(Recipe.created_at.desc()).all()


def get_recipe(recipe_id):
    """Retorna uma receita específica"""
    return db.session.get(Recipe, recipe_id)


def get_all_products():
    """Retorna todos os produtos ativos"""
    return Product.query.filter(Product.active.is_(True)).order_by(Product.name).all()
