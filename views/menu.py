from flask import Blueprint
from flask_restful import Resource, Api
from webargs import fields, validate, ValidationError
from utils.resp import to_dict_result
from utils.parser import parser
from models import Menu

menu_bp = Blueprint('menu', __name__)
menu_api = Api(menu_bp)


def must_exist_in_db(mid: int):
    if not Menu.query.get(mid):
        raise ValidationError(f'menu id {mid} does not exist')


menu_args = {
    'name': fields.Str(required=True, allow_none=False, validate=validate.Length(min=1, max=32)),
    'level': fields.Int(required=True, allow_none=False, validate=validate.Range(min=1, max=3)),
    'path': fields.Str(),
    'parent_id': fields.Int(required=True, allow_none=False, validate=must_exist_in_db)
}


# def get_menu_tree(menu: Menu):
#     """递归生成菜单树"""
#     menu_dict = menu.to_dict()
#     if menu.children:
#         menu_dict['children'] = []
#         for child in menu.children:
#             child_dict = get_menu_tree(child)
#             menu_dict['children'].append(child_dict)
#     return menu_dict

class Menus(Resource):
    def get(self):
        # print('获取菜单树')
        # root_menu = Menu.query.filter(Menu.level == 0).first()
        # return to_dict_result(0, root_menu.to_dict()) if root_menu else (to_dict_result(3005), 404)
        menus = Menu.query.filter(Menu.level == 1).all()
        return to_dict_result(0, list(map(lambda x: x.to_dict(), menus))) if menus else (to_dict_result(3005), 404)

    # def post(self):
    #     args = parser.parse(menu_args, request, location='json_or_form')
    #     if Menu.query.filter(Menu.name == args.get('name')).first():
    #         return to_dict_result(3006, message='该菜单名已存在'), 409
    #     db.session.add(Menu(**args))
    #     db.session.commit()
    #     return to_dict_result(0), 201


# class MenuById(Resource):
#     def get(self, mid: int):
#         menu = Menu.query.get(mid)
#         return to_dict_result(0, menu.to_dict()) if menu else (to_dict_result(3005), 404)
#
#     def put(self, mid: int):
#         args = parser.parse(menu_args, request, location='json_or_form')
#         if Menu.query.filter(Menu.name == args.get('name'), Menu.id != mid).first():
#             return to_dict_result(3006, message='该菜单名已存在'), 409
#         Menu.query.filter(Menu.id == mid).update(args)
#         db.session.commit()
#         return to_dict_result(0)
#
#     def delete(self, mid: int):
#         Menu.query.filter(Menu.id == mid).delete()
#         db.session.commit()
#         return to_dict_result(0)


menu_api.add_resource(Menus, '/menus')
# menu_api.add_resource(MenuById, '/menus/<int:mid>')







