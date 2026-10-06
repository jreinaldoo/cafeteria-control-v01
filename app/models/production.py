from datetime import datetime
from decimal import Decimal

from app import db


class Production(db.Model):
    __tablename__ = "productions"

    id = db.Column(db.Integer, primary_key=True)
    production_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="ABERTA")  # ABERTA, FINALIZADA
    notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    finalized_at = db.Column(db.DateTime, nullable=True)

    items = db.relationship("ProductionItem", back_populates="production", cascade="all, delete-orphan")


class ProductionItem(db.Model):
    __tablename__ = "production_items"

    id = db.Column(db.Integer, primary_key=True)
    production_id = db.Column(db.Integer, db.ForeignKey("productions.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity_produced = db.Column(db.Numeric(10, 3), nullable=False)
    quantity_sold = db.Column(db.Numeric(10, 3), nullable=False, default=Decimal("0"))
    quantity_lost = db.Column(db.Numeric(10, 3), nullable=False, default=Decimal("0"))

    production = db.relationship("Production", back_populates="items")
    product = db.relationship("Product")
