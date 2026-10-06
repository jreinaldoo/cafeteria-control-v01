import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret-key"),
        SQLALCHEMY_DATABASE_URI=os.getenv(
            "DATABASE_URL",
            f"sqlite:///{Path(app.instance_path) / 'cafeteria.db'}",
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    @app.template_filter("number_format")
    def number_format(value):
        try:
            number = float(value or 0)
            if number.is_integer():
                return f"{int(number)}"
            return f"{number:.3f}".rstrip("0").rstrip(".")
        except (TypeError, ValueError):
            return str(value)

    from app.routes.dashboard import dashboard_bp
    from app.routes.products import products_bp
    from app.routes.sales import sales_bp
    from app.routes.purchases import purchases_bp
    from app.routes.stock import stock_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(products_bp, url_prefix="/produtos")
    app.register_blueprint(sales_bp, url_prefix="/vendas")
    app.register_blueprint(purchases_bp, url_prefix="/compras")
    app.register_blueprint(stock_bp, url_prefix="/estoque")

    with app.app_context():
        from app import models  # noqa: F401
        db.create_all()
        from app.services.seed_service import seed_initial_data
        seed_initial_data()

    return app
