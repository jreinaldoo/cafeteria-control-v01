from datetime import datetime
from decimal import Decimal

from app import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    name = db.Column(db.String(150), nullable=False, unique=True)
    cost = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    sale_price = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    stock_quantity = db.Column(db.Numeric(10, 3), nullable=False, default=Decimal("0"))
    min_stock = db.Column(db.Numeric(10, 3), nullable=False, default=Decimal("0"))
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = db.relationship("Category", back_populates="products")
    sale_items = db.relationship("SaleItem", back_populates="product")
    purchase_items = db.relationship("PurchaseItem", back_populates="product")
    stock_movements = db.relationship("StockMovement", back_populates="product")

    @property
    def gross_profit(self):
        return Decimal(self.sale_price or 0) - Decimal(self.cost or 0)

    @property
    def margin_percent(self):
        price = Decimal(self.sale_price or 0)
        if price <= 0:
            return Decimal("0")
        return (self.gross_profit / price) * Decimal("100")

    @property
    def low_stock(self):
        return Decimal(self.stock_quantity or 0) <= Decimal(self.min_stock or 0)
