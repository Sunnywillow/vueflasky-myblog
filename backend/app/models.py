from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from flask import url_for, current_app
from datetime import datetime, timedelta
import jwt
from hashlib import md5

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
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)  # 添加打印对象

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        '''头像'''
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)


    def to_dict(self, include_email=False):  # 默认参数为False
        data = {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'location': self.location,
            'about_me': self.about_me,
            'member_since': self.member_since.isoformat() + 'Z',
            'last_seen': self.last_seen.isoformat() + 'Z',
            '_links': {
                'self': url_for('api.get_user', id=self.id),
                'avatar': self.avatar(128)
            }
        }
        if include_email:
            data['email'] = self.email
        return data

    def from_dict(self, data, new_user=True):  # 默认新用户为真
        for field in ['username', 'email', 'name', 'location', 'about_me']:  # 遍历表单中的username 和 email
            # 如果 前端发送过来的表单中的数据 存在于data中
            if field in data:
                # 将对应的json实例的field值存入data中
                setattr(self, field, data[field])
        # 如果还是新用户 且 有设置密码
        if new_user and 'password' in data:
            # 将密码字段也加入到data中(set_password为hash值)
            self.set_password(data['password'])

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def get_jwt(self, expires_in=3600):  # 将get_token方法修改为get_jwt()方法
        now = datetime.utcnow() # 当前时间
        payload = {
            'user_id': self.id,
            'name': self.name if self.name else self.username,  # 如果用户的名字存在则放name,否则username
            'exp': now + timedelta(seconds=expires_in),
            'iat': now
        }
        return jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')  # 返回一个字段payload,先进行编码再解码成utf-8格式



    # 静态方法
    @staticmethod
    def verify_jwt(token):  # 使用jwt的decode解码
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithm=['HS256'])
        except (jwt.exceptions.ExpiredSignatureError, jwt.exceptions.InvalidSignatureError) as e:
            # Token过期,或者被人修改,name签名验证也会失败
            return None
        return  User.query.get(payload.get('user_id'))  # 返回user_id



