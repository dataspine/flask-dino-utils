from flask import request, jsonify
from functools import update_wrapper
from validators import validate_param_internal, NUMERIC_STRING_VALIDATOR, MIN_VALIDATOR
from marshmallow import Schema, fields


class PaginationSchema(Schema):
    per_page = fields.Integer()
    page = fields.Integer()
    items = fields.List(fields.Nested(Schema))

    def set_items_objects(self, object_class):
        self.items = fields.List(fields.Nested(object_class))

def paginable():
    def decorator(func):
        def wrapper(*args, **kwargs):
            validate_param_internal(request.args, "page", [(NUMERIC_STRING_VALIDATOR,), (MIN_VALIDATOR, 1)])
            validate_param_internal(request.args, "per_page", [(NUMERIC_STRING_VALIDATOR,), (MIN_VALIDATOR, 1)])
            return func(*args, **kwargs)
        return update_wrapper(wrapper, func)
    return decorator


def paginated_response(args, data, schema_class):
    data = data.paginate(page=int(args.get("page", 1)), per_page=(int(args.get("per_page", 100))), error_out=False)
    pagination_schema = PaginationSchema()
    pagination_schema.set_items_objects(schema_class)
    response = pagination_schema.dump(data).data
    return jsonify(response)



