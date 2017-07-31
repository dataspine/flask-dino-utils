from werkzeug.exceptions import BadRequest
from functools import update_wrapper
from validators import validate_param_internal, VALID_VALUES_VALIDATOR
from flask import request

VALID_SORT_DIRECTIONS = ["asc", "desc"]


def _validate_sorting_parameters(args, object_type):
    validate_param_internal(request.args, "sort_dir", [(VALID_VALUES_VALIDATOR, VALID_SORT_DIRECTIONS)])
    sort_field = request.args.get("sort_field", None)
    if sort_field is not None and sort_field not in object_type.__table__.columns.keys():
        raise BadRequest('The sort_field %s is not a valid value' % sort_field)


def sortable(object_type):
    def decorator(func):
        def wrapper(*args, **kwargs):
            _validate_sorting_parameters(request.args, object_type)
            return func(*args, **kwargs)
        return update_wrapper(wrapper, func)
    return decorator


def sort(args, data):
    sort_field = args.get("sort_field", None)
    if sort_field is None:
        return data
    else:
        data = data.order_by("{sort_field} {sort_dir}".format(sort_field=sort_field,
                                                           sort_dir=args.get('sort_dir', 'asc')))
    return data
