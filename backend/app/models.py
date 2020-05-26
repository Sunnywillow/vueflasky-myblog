from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from flask import url_for
from datetime import datetime, timedelta
import base64
import os


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data


class User(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    token = db.Column(db.String(32), index=True, unique=True)  # token
    token_expiration = db.Column(db.DateTime)  # 过期时间

    def __repr__(self):
        return '<User {}>'.format(self.username)  # 添加打印对象

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_email=False):  # 默认参数为False
        data = {
            'id': self.id,
            'username': self.username,
            '_links': {
                'self': url_for('api.get_user', id=self.id)
            }
        }
        if include_email:
            data['email'] = self.email
        return data

    def from_dict(self, data, new_user=True):  # 默认新用户为真
        for field in ['username', 'email']:  # 遍历表单中的username 和 email
            # 如果 前端发送过来的表单中的数据 存在于data中
            if field in data:
                # 将对应的json实例的field值存入data中
                setattr(self, field, data[field])
        # 如果还是新用户 且 有设置密码
        if new_user and 'password' in data:
            # 将密码字段也加入到data中(set_password为hash值)
            self.set_password(data['password'])

    def get_token(self, expires_in=3600):
        now = datetime.utcnow() # 当前时间
        # 如果token存在且过期时间大于当前时间差
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        # 否则 生成token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        # 生成过期时间
        self.token_expiration = now + timedelta(seconds=expires_in)
        # 更新用户
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    # 静态方法
    @staticmethod
    def check_token(token):
        # 查询数据库中值为token的实例user
        user = User.query.filter_by(token=token).first()
        # 如果不存在或已经过期
        if user is None or user.token_expiration < datetime.utcnow():
            # 返回无
            return None
        # 否则返回user
        return user

