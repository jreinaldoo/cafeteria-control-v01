from datetime import date, datetime
from decimal import Decimal

from app import db


class Purchase(db.Model):
    __tablename__ = "purchases"

    id = db.Column(db.Integer, primary_key=True)
    supplier = db.Column(db.String(150), nullable=True)
    purchase_date = db.Column(db.Date, nullable=False, default=date.today)
    total = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    items = db.relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")


class PurchaseItem(db.Model):
    __tablename__ = "purchase_items"

    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey("purchases.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Numeric(10, 3), nullable=False)
    unit_cost = db.Column(db.Numeric(10, 2), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)

    purchase = db.relationship("Purchase", back_populates="items")
    product = db.relationship("Product", back_populates="purchase_items")
