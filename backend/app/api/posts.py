from app.api import bp
from app.api.auth import token_auth
from flask import request,jsonify, url_for, g
from app.api.errors import bad_request, error_response
from app.models import Post
from app.extensions import db


@bp.route('/posts', methods=['POST'])
@token_auth.login_required
def create_post():
    '''添加一篇文章'''
    # 获取json
    data = request.get_json()
    if not data:
        return bad_request('You must post JSON data.')
    message = {}
    # 如果任意两种方式都没拿到title
    if 'title' not in data or not data.get('title'):
        message['title'] = 'Title is required.'
    # 标题字符串长度超过255
    elif len(data.get('title')) > 255:
        message['title'] = 'Title must less than 255 characters.'
    # 验证data中的body数据
    if 'body' not in data or not data.get('body'):
        message['body'] = 'Body is required.'
    # 最后验证一下messge列表是否为真
    if message:
        return bad_request(message)

    # 生成post实例
    post = Post()
    # 将表单中的数据变成post的属性
    post.from_dict(data)
    post.author = g.current_user
    # 通过auth.py 中 verify_token()传递过来的 (同一个request中,
    # 需要先进行Token 认证
    db.session.add(post)
    db.session.commit()
    # todict使post的属性变成字典 再变成json格式赋值给response
    response = jsonify(post.todict())
    response.status_code = 201
    # HTTP协议要求201响应包含一个值为新资源URL的Location头部
    response.headers['Location'] = url_for('api.get_post', id=post.id)
    return response




@bp.route('/posts', methods=['GET'])
def get_posts():
    '''返回文章集合, 分页'''
    #页数  从请求中获取page的信息
    page = request.args.get('page', 1, type=int)
    # 每页
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    # data 使用to_collection_dict()方法 查询参数page或per_page
    data = Post.to_collection_dict(Post.query.order_by(Post.timestamp.desc()), page, per_page, 'api.get_posts')
    return jsonify(data)


@bp.route('/posts/<int:id>', methods=['GET'])
def get_post(id):
    '''返回一篇文章'''
    post = Post.query.get_or_404(id)
    post.views += 1
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_dict())

@bp.route('/posts/<int:id>', methods=['PUT'])
def update_post(id):
    '''修改一篇文章'''
    # 生成post实例
    post = Post.query.get_or_404(id)
    # 验证身份
    if g.current_user != post.author:
        return error_response(403)

    # 将前端发送的json数据转化为python对象
    data = request.get_json()
    # 如果data不存在
    if not data:
        return bad_request('You must post JSOn data.')
    # 创建message容器
    message = {}
    # 如果data中不存在title 或 data没取到title
    if 'title' not in data or not data.get('title'):
        message['title'] = 'Title is required.'
    # 拿到的title的长度如果大于255
    elif len(data.get('title')) > 255:
        message['title'] = 'Title must less than 255 characters.'
    if 'body' not in data or not data.get('body'):
        message['body'] = 'Body is required.'
    if message:
        return bad_request(message)

    # 将post实例的data属性变成字典的形式
    post.from_dict(data)
    # 存入数据库
    db.session.commit()
    # 将post实例变成字典的形式 再转化成json格式发给前端
    return jsonify(post.to_dict())


# 用户必须通过Token认证, 而且他还必须是该博客文章的作者才允许删除
@bp.route('/posts/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_post(id):
    '''删除一篇文章'''
    post = Post.query.get_or_404(id)
    # 验证身份
    if g.current_user != post.author:
        return error_response(403)
    db.session.delete(id)
    db.session.commit()
    return '', 204



