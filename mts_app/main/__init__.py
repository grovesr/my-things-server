from flask import Blueprint

bp = Blueprint('main', __name__)

from mts_app.main import routes