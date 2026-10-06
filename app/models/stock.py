from datetime import datetime
from decimal import Decimal

from app import db


class StockMovement(db.Model):
    __tablename__ = "stock_movements"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Numeric(10, 3), nullable=False)
    reference_type = db.Column(db.String(30), nullable=True)
    reference_id = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    product = db.relationship("Product", back_populates="stock_movements")
