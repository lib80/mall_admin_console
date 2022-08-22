from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class BaseModel:
    create_time = db.Column(db.DateTime, default=datetime.now, doc='创建时间')
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, doc='更新时间')


class Admin(db.Model, BaseModel):
    __tablename__ = 't_admin'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_code = db.Column(db.String(32), unique=True, nullable=False, doc='账号')
    _password = db.Column('password', db.String(128), nullable=False, doc='密码')
    mobile = db.Column(db.String(11), unique=True, nullable=False, doc='手机号')
    role_id = db.Column(db.Integer, db.ForeignKey('t_role.id', ondelete='SET NULL', onupdate='CASCADE'))
    status = db.Column(db.Integer, nullable=False, default=1, doc='数据状态 1正常 0停用')
    login_time = db.Column(db.DateTime, default=datetime.now, doc='最后一次登录时间')

    def to_dict(self):
        return {
            'id': self.id,
            'admin_code': self.admin_code,
            'mobile': self.mobile,
            'status': self.status,
            'role_id': self.role_id,
            'role_name': self.role.name,
        }

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, pwd: str):
        self._password = generate_password_hash(pwd)

    def check_password(self, pwd: str) -> bool:
        return check_password_hash(self._password, pwd)


r2m = db.Table('t_role_menu',
    db.Column('role_id', db.Integer, db.ForeignKey('t_role.id', ondelete='CASCADE'), primary_key=True),
    db.Column('menu_id', db.Integer, db.ForeignKey('t_menu.id', ondelete='CASCADE'), primary_key=True)
)


class Role(db.Model):
    __tablename__ = 't_role'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), unique=True, nullable=False, doc='角色名')
    description = db.Column(db.String(64), doc='描述')
    admins = db.relationship('Admin', backref='role')
    menus = db.relationship('Menu', secondary=r2m, backref=db.backref('roles'))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'menus': list(map(lambda x: x.to_dict(), self.menus))
        }


class Menu(db.Model):
    __tablename__ = 't_menu'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), unique=True, nullable=False, doc='菜单名')
    level = db.Column(db.Integer, nullable=False, doc='级别 值越小，级别越大')
    path = db.Column(db.String(32), doc='url路径')
    parent_id = db.Column(db.Integer, db.ForeignKey('t_menu.id', ondelete='CASCADE'), doc='父级id')
    children = db.relationship('Menu')

    def to_dict(self):
        data =  {
            'id': self.id,
            'name': self.name,
            'level': self.level,
            'path': self.path,
            'parent_id': self.parent_id
        }
        if self.children:
            data['children'] = list(map(lambda x: x.to_dict(), self.children))
        return data


