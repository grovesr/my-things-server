from flask import Blueprint

bp = Blueprint('admin', __name__)

from mts_app.admin import routes