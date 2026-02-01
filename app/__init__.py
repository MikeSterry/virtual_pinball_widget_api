from flask import Flask

from app.configs.settings import Settings
from app.controllers.api_controller import api_bp
from app.controllers.table_widget_controller import table_widget_bp
from app.controllers.backglass_widget_controller import backglass_widget_bp
from app.controllers.health_controller import health_bp
from app.controllers.vpsdb_sync_controller import vpsdb_sync_bp


def create_app() -> Flask:
    """Application factory."""
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Load settings into app config
    settings = Settings.from_env()
    app.config["SETTINGS"] = settings

    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(vpsdb_sync_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(table_widget_bp, url_prefix="/widgets/tables")
    app.register_blueprint(backglass_widget_bp, url_prefix="/widgets/backglasses")

    return app