from flask import request, jsonify
from functools import update_wrapper
from validators import validate_param_internal, NUMERIC_STRING_VALIDATOR, MIN_VALIDATOR
from marshmallow import Schema, fields


def __create_pagination_schema(object_class):
    class PaginationSchema(Schema):
        per_page = fields.Integer()
        page = fields.Integer()
        items = fields.List(fields.Nested(object_class))
        pages = fields.Integer()
        total = fields.Integer()
        has_prev = fields.Boolean()
        has_next = fields.Boolean()
        next_num = fields.Integer()
        prev_num = fields.Integer()
    return PaginationSchema()


def _validate_pagination_parameters(args):
    validate_param_internal(args, "page", [(NUMERIC_STRING_VALIDATOR,), (MIN_VALIDATOR, 1)])
    validate_param_internal(args, "per_page", [(NUMERIC_STRING_VALIDATOR,), (MIN_VALIDATOR, 1)])


def paginable():
    def decorator(func):
        def wrapper(*args, **kwargs):
            _validate_pagination_parameters(request.args)
            return func(*args, **kwargs)
        return update_wrapper(wrapper, func)
    return decorator


def paginated_response(args, data, schema_class):
    data = data.paginate(page=int(args.get("page", 1)), per_page=(int(args.get("per_page", 100))), error_out=False)
    pagination_schema = __create_pagination_schema(schema_class)
    response = pagination_schema.dump(data).data
    return jsonify(response)



