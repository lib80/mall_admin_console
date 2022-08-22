import random
from flask import Blueprint, request, jsonify
from flask_restful import Resource, Api
from webargs import fields, validate
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies, get_jwt_identity, jwt_required
from utils.resp import to_dict_result
from utils.parser import parser
from utils.sms import send_sms
from utils.nosql_redis import redis_conn
from utils.const import SMS_CODE_EXPIRES
from utils.limiter import limiter
from models import Admin, db
from views.role import must_exist_in_db

admin_bp = Blueprint('admin', __name__)
admin_api = Api(admin_bp)

sms_args = {'mobile': fields.Str(required=True, allow_none=False, validate=validate.Regexp(r'1[3578]\d{9}'))}
login_args = {
    **sms_args,
    'password': fields.Str(required=True, allow_none=False, validate=validate.Regexp(r'^(?:(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])).{6,16}$')),
    'captcha': fields.Str(required=True, allow_none=False)
}
admin_args = {
    **login_args,
    'admin_code': fields.Str(required=True, allow_none=False, validate=validate.Length(min=1, max=32)),
    'role_id': fields.Int(required=True, allow_none=False, validate=must_exist_in_db)
}


class Admins(Resource):
    # method_decorators = [jwt_required()]

    def get(self):
        """获取管理员账号列表"""
        admins = Admin.query.all()
        return to_dict_result(0, list(map(lambda x: x.to_dict(), admins))) if admins else (to_dict_result(3005), 404)

    def post(self):
        """创建管理员账号"""
        args = parser.parse(admin_args, request, location='json_or_form')
        if Admin.query.filter(Admin.admin_code == args.get('admin_code')).first():
            return to_dict_result(3006, message='该账号名已被占用'), 409
        if Admin.query.filter(Admin.mobile == args.get('mobile')).first():
            return to_dict_result(3006, message='该手机号已注册'), 409
        db.session.add(Admin(**args))
        db.session.commit()
        return to_dict_result(0), 201


class AdminById(Resource):
    def get(self, aid: int):
        admin = Admin.query.get(aid)
        return to_dict_result(0, admin.to_dict()) if admin else (to_dict_result(3005), 404)

    def put(self, aid: int):
        """修改指定账号信息"""
        args = parser.parse(admin_args, request, location='json_or_form')
        if Admin.query.filter(Admin.admin_code == args.get('admin_code'), Admin.id != aid).first():
            return to_dict_result(3006, message='该账号名已被占用'), 409
        if Admin.query.filter(Admin.mobile == args.get('mobile'), Admin.id != aid).first():
            return to_dict_result(3006, message='该手机号已注册'), 409
        Admin.query.filter(Admin.id == aid).update(args)
        db.session.commit()
        return to_dict_result(0)

    def delete(self, aid: int):
        Admin.query.filter(Admin.id == aid).delete()
        db.session.commit()
        return to_dict_result(0)


@admin_bp.post('/login/captcha')
@limiter.limit('5/minute', error_message='发送频率超过限制，请稍后再试')
def sms_captcha():
    """发送短信验证码"""
    args = parser.parse(sms_args, request, location='json_or_form')
    mobile = args.get('mobile')
    if not Admin.query.filter(Admin.mobile == mobile).first():
        return to_dict_result(3005, message='账号未找到'), 404
    captcha = str(random.randint(100000, 999999))
    resp = send_sms(mobile, captcha)
    success = redis_conn.setex(f'captcha_{mobile}', SMS_CODE_EXPIRES, captcha)
    return to_dict_result(0) if success else (to_dict_result(5001), 500)


@admin_bp.post('/login')
def login():
    args = parser.parse(login_args, request, location='json_or_form')
    mobile = args.get('mobile')
    admin = Admin.query.filter(Admin.mobile == mobile).first()
    if not (admin and admin.check_password(args.get('password'))):
        return to_dict_result(400, message='手机号或密码错误')
    real_captcha = redis_conn.get(f'captcha_{mobile}')
    if args.get('captcha') != real_captcha:
        return to_dict_result(400, message='验证码错误')
    response = jsonify(to_dict_result(0, data=admin.to_dict(), message='登陆成功'))
    access_token = create_access_token(identity=admin.id)
    set_access_cookies(response, access_token)
    return response
    # return to_dict_result(0, data={'token': generate_token(admin.id)})


@admin_bp.post('/logout')
# @jwt_required()
def logout():
    response = jsonify(to_dict_result(0, message='退出成功'))
    unset_jwt_cookies(response)
    return response


@admin_bp.post('/admin/change_status')
def change_status():
    """禁用/启用账号"""
    args = parser.parse({'id': fields.Int(required=True, allow_none=False)}, request, location='json_or_form')
    admin = Admin.query.get(args.get('id'))
    if not admin:
        return to_dict_result(3005, message='账号未找到'), 404
    admin.status = not admin.status
    db.session.commit()
    return to_dict_result(0)


admin_api.add_resource(Admins, '/admins')
admin_api.add_resource(AdminById, '/admins/<int:aid>')

