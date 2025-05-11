from flask import Flask
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates', static_folder='static')

def register_routes():
    from app.routes import api_routes, web_routes
    api_routes.register_routes(app)
    web_routes.register_routes(app)
