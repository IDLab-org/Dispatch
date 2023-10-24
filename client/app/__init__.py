from flask import Flask, session
from config import Config
from flask_qrcode import QRcode
import logging

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    QRcode(app)

    if __name__ != "__main__":
        gunicorn_logger = logging.getLogger("gunicorn.error")
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

    from app.errors import bp as errors_bp

    app.register_blueprint(errors_bp)

    from app.routes.main import bp as main_bp

    app.register_blueprint(main_bp)

    return app
