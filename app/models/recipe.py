from datetime import datetime

from app import db


class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("RecipeItem", backref="recipe", lazy=True, cascade="all, delete-orphan")

    @property
    def total_cost(self):
        """Custo total da receita somando todos os itens"""
        return sum(item.calculated_cost for item in self.items)

    def __repr__(self):
        return f"<Recipe {self.name}>"


class RecipeItem(db.Model):
    __tablename__ = "recipe_items"

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity_used = db.Column(db.Numeric(10, 3), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product", backref="recipe_items")

    @property
    def calculated_cost(self):
        """Calcula o custo proporcional do item na receita"""
        if not self.product or self.product.unit_quantity == 0:
            return 0
        # Custo proporcional: (quantidade_usada / quantidade_por_unidade) * custo_total
        ratio = float(self.quantity_used) / float(self.product.unit_quantity)
        return ratio * float(self.product.cost)

    def __repr__(self):
        return f"<RecipeItem {self.product.name} - {self.quantity_used}>"
