from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES
from app.api import bp


# 错误响应
def error_response(status_code, message=None):
    # 用werkzeug.http包的方法获取到的对应键值
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    # 如果还有message参数 则把message也加入到payload字典中
    if message:
        payload['message'] = message
    # 将payload变成json对象 赋值给response
    response = jsonify(payload)
    # 将状态码作为一个属性赋值给response
    response.status_code = status_code
    return response


def bad_request(message):
    '''最常用的错误 400: 错误的请求'''
    return error_response(400, message)


@bp.app_errorhandler(404)
def not_found_error(error):
    return error_response(404)


@bp.app_errorhandler(500)
def internal_error(error):
    return error_response(500)
