from flask import g, jsonify
from app import db
from app.api import bp
from app.api.auth import basic_auth


@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    # 生成token
    token = g.current_user.get_jwt()
    # 保存到数据库
    # 每次用户登录(即成功获取 JWT后), 更新 last_seen 时间
    g.current_user.ping()
    db.session.commit()
    return jsonify({'token': token})


