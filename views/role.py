from flask import Blueprint, request
from flask_restful import Resource, Api
from webargs import fields, validate, ValidationError
from utils.resp import to_dict_result
from utils.parser import parser
from models import Role, Menu, db
from views import menu

role_bp = Blueprint('role', __name__)
role_api = Api(role_bp)


def must_exist_in_db(rid: int):
    if not Role.query.get(rid):
        raise ValidationError(f'role id {rid} does not exist')


role_args = {
    'name': fields.Str(required=True, allow_none=False, validate=validate.Length(min=1, max=32)),
    'description': fields.Str(),
    'menu_ids': fields.List(fields.Int(validate=menu.must_exist_in_db), required=True, allow_none=False, validate=validate.Length(min=1))
}


class Roles(Resource):
    def get(self):
        """获取角色列表"""
        roles = Role.query.all()
        return to_dict_result(0, list(map(lambda x: x.to_dict(), roles))) if roles else (to_dict_result(3005), 404)

    def post(self):
        """创建角色"""
        args = parser.parse(role_args, request, location='json_or_form')
        if Role.query.filter(Role.name == args.get('name')).first():
            return to_dict_result(3006, message='该角色名已存在'), 409
        menu_ids = args.get('menu_ids')
        menus = [Menu.query.get(mid) for mid in menu_ids]
        role = Role(name=args.get('name'), description=args.get('description'), menus=menus)
        db.session.add(role)
        db.session.commit()
        return to_dict_result(0), 201


class RoleById(Resource):
    def get(self, rid: int):
        role = Role.query.get(rid)
        return to_dict_result(0, role.to_dict()) if role else (to_dict_result(3005), 404)

    def put(self, rid: int):
        args = parser.parse(role_args, request, location='json_or_form')
        if Role.query.filter(Role.name == args.get('name'), Role.id != rid).first():
            return to_dict_result(3006, message='该角色名已存在'), 409
        menu_ids = args.get('menu_ids')
        menus = [Menu.query.get(mid) for mid in menu_ids]
        role = Role.query.get(rid)
        role.name = args.get('name')
        role.description = args.get('description')
        role.menus = menus
        db.session.commit()
        return to_dict_result(0)

    def delete(self, rid: int):
        Role.query.filter(Role.id == rid).delete()
        db.session.commit()
        return to_dict_result(0)


role_api.add_resource(Roles, '/roles')
role_api.add_resource(RoleById, '/roles/<int:rid>')







