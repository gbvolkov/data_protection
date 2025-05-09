from flask import Flask
import config
from routes import main_bp

from logger_factory import set_logging
import logging

logging.basicConfig(level=logging.WARNING)
set_logging("anonimizer", logging.WARNING)
#logger = logging.getLogger("anonimizer")

def create_app():
    app = Flask(__name__)
    #app.config.from_object(Config)
    app.secret_key = config.SECRET_APP_KEY
    # Register Blueprints
    app.register_blueprint(main_bp)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5002, debug=False)