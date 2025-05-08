from flask import Flask
import config
from routes import main_bp


def create_app():
    app = Flask(__name__)
    #app.config.from_object(Config)

    # Register Blueprints
    app.register_blueprint(main_bp)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)