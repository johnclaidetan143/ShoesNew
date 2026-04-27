from flask import Flask
from config import Config
from app.extensions import db, jwt, bcrypt
from app.routes.auth import auth_bp
from app.routes.products import products_bp
from app.routes.cart import cart_bp
from app.routes.orders import orders_bp
from app.routes.user import user_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    for blueprint in [auth_bp, products_bp, cart_bp, orders_bp, user_bp]:
        app.register_blueprint(blueprint)

    with app.app_context():
        db.create_all()

    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Resource not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {"error": "Internal server error"}, 500

    @app.get("/health")
    def health_check():
        return {"status": "healthy"}

    return app
