code_message = {
    0: 'ok',
    400: '参数异常',
    2000: '未登录',
    2001: '当前用户无此权限',
    2002: '账号或密码错误',
    2003: '未知错误',
    2004: '操作不支持',
    3000: '数据异常',
    3001: '新增数据失败',
    3002: '删除数据失败',
    3003: '修改数据失败',
    3004: '查询数据失败',
    3005: '查无数据',
    3006: '数据冲突',
    5000: '服务异常',
    5001: '未知错误'
}


def to_dict_result(code: int, data=None, message=None) -> dict:
    dict_result = {'code': code, 'message': message if message else code_message.get(code)}
    if data:
        dict_result['data'] = data
    return dict_result




