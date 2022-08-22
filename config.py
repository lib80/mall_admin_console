import datetime

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:xxx@localhost:3306/mall_admin_console'
SQLALCHEMY_TRACK_MODIFICATIONS = True
# SQLALCHEMY_ECHO = True
JWT_SECRET_KEY = 'xxx'
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=1)
# JWT_HEADER_TYPE = 'Bearer' # header中token字符串的前缀
JWT_TOKEN_LOCATION = ["cookies"]
JWT_COOKIE_SECURE = True

JSON_AS_ASCII = False
DEBUG = True
