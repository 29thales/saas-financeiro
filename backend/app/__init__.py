from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    with app.app_context():
        from app.routes.auth import auth_bp
        from app.routes.accounts import accounts_bp
        from app.routes.expenses import expenses_bp
        from app.routes.uploads import uploads_bp
        from app.routes.splits import splits_bp
        from app.routes.reports import reports_bp
        from app.routes.views import views_bp
        from app.routes.admin import admin_bp
        from app.routes.fixed_expenses import fixed_bp
        from app.routes.settings import settings_bp
        from app.routes.balance import balance_bp
        from app.routes.card_discounts import discounts_bp


        app.register_blueprint(auth_bp)
        app.register_blueprint(accounts_bp)
        app.register_blueprint(expenses_bp)
        app.register_blueprint(uploads_bp)
        app.register_blueprint(splits_bp)
        app.register_blueprint(reports_bp)
        app.register_blueprint(views_bp)
        app.register_blueprint(admin_bp) 
        app.register_blueprint(fixed_bp)
        app.register_blueprint(settings_bp)
        app.register_blueprint(balance_bp)
        app.register_blueprint(discounts_bp)

    return app