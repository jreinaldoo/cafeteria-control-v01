from app import create_app, db


def test_app_creates_seed_products(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
    })
    with app.app_context():
        from app.models import Product
        assert Product.query.count() == 9
        assert Product.query.filter_by(name="Pão de Queijo").first().sale_price == 5
