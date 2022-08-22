import datetime
from flask import Flask, request
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, get_jwt, get_jwt_identity, create_access_token, set_access_cookies, verify_jwt_in_request
from utils.limiter import limiter
from models import db


app = Flask(__name__)
app.config.from_pyfile('config.py')
# for k, v in app.config.items():
#     print(k, v)
jwt = JWTManager(app)
limiter.init_app(app)

db.init_app(app)
migrate = Migrate(app, db)

from views.menu import menu_bp
app.register_blueprint(menu_bp)

from views.role import role_bp
app.register_blueprint(role_bp)

from views.admin import admin_bp
app.register_blueprint(admin_bp)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.before_request
def check_token():
    """这是一个用于检验token的拦截器"""
    white_list = ['/login', '/login/captcha']
    if request.path not in white_list:
        verify_jwt_in_request()


@app.after_request
def refresh_expiring_jwts(response):
    """若请求后发现距离token过期不到半小时则刷新token"""
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.datetime.now()
        target_timestamp = datetime.datetime.timestamp(now + datetime.timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response


if __name__ == '__main__':
    app.run()
