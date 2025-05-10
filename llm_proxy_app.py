from flask import Flask
import config
#import os
#os.environ["LANGCHAIN_ENDPOINT"]="https://api.smith.langchain.com"
#os.environ["LANGCHAIN_TRACING_V2"] = "true"

from routes import main_bp
from logger_factory import setup_logging



def create_app():
    app = Flask(__name__)
    #app.config.from_object(Config)
    app.secret_key = config.SECRET_APP_KEY
    # Register Blueprints
    app.register_blueprint(main_bp)

    return app


if __name__ == '__main__':
    setup_logging("anonimizer_web")
    app = create_app()
    app.run(host='0.0.0.0', port=5002, debug=False)