from flask import Blueprint

bp = Blueprint('api', __name__)

# 防止循环导入, ping.py也会导入bp
from app.api import ping, users, tokens
