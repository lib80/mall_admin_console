import typing
import marshmallow as ma
from flask import abort, make_response, jsonify
from webargs.flaskparser import FlaskParser
from webargs.core import Request


def _strip_whitespace(value):
    if isinstance(value, str):
        value = value.strip()
        # you'll be getting a MultiDictProxy here potentially, but it should work
    elif isinstance(value, typing.Mapping):
        return {k: _strip_whitespace(value[k]) for k in value}
    elif isinstance(value, (list, set)):
        return type(value)(map(_strip_whitespace, value))
    return value


class CustomParser(FlaskParser):
    """扩展原生的parser的功能，实现类似 trim=True 的效果， pre_load是webargs提供的一个扩展接口"""
    def pre_load(
            self,
            location_data: typing.Mapping,
            *,
            schema: ma.Schema,
            req: Request,
            location: str,
    ) -> typing.Mapping:
        return _strip_whitespace(location_data)


parser = CustomParser()


@parser.error_handler
def handle_error(error, req, schema, *, error_status_code, error_headers):
    abort(make_response(jsonify(code=400, message=error.messages), 400))