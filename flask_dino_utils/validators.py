from werkzeug.exceptions import BadRequest, InternalServerError
from functools import update_wrapper
from flask import request
import re

TYPE_VALIDATOR = 1
MIN_VALIDATOR = 2
MAX_VALIDATOR = 3
REGEX_VALIDATOR = 4
VALID_VALUES_VALIDATOR = 5
NUMERIC_STRING_VALIDATOR = 6

REQUEST_QUERY_PARAMS = "ARGS"
REQUEST_BODY = "BODY"


def __validate_type(param_key, param_value, type):
    if isinstance(param_value, type):
        return param_value
    else:
        raise BadRequest("The value %s for param %s is not of type %s" % (str(param_value), param_key, type))


def __validate_min(param_key, param_value, min):
    if param_value >= min:
        return param_value
    else:
        raise BadRequest("The value %s for param %s is less than %s" % (str(param_value), param_key, min))


def __validate_max(param_key, param_value, max):
    if param_value <= max:
        return param_value
    else:
        raise BadRequest("The value %s for param %s is greater than %s" % (str(param_value), param_key, max))


def __validate_regex(param_key, param_value, regex):
    if re.match(regex, param_value):
        return param_value
    else:
        raise BadRequest("The value %s for param %s does not match to regex %s" % (str(param_value), param_key, regex))


def __validate_valid_values(param_key, param_value, valid_values):
    if param_value in valid_values:
        return param_value
    else:
        raise BadRequest("The value %s for param %s is not a valid value. Valid values: %s"
                         % (param_value, param_key, ', '.join(str(valid) for valid in valid_values)))


def __validate_numeric_string(param_key, param_value):
    try:
        float(param_value)
        return param_value
    except:
        raise BadRequest("The value %s for param %s is not a valid numeric value" % (param_value, param_key))


def validate_param_internal(data, param_key, param_tuple, required=False):
    param = data.get(param_key, None)
    if param is None:
        if not required:
            return None
        else:
            raise BadRequest("The param %s is mandatory" % param_key)

    for ituple in param_tuple:
        if ituple[0] == TYPE_VALIDATOR:
            param = __validate_type(param_key, param, ituple[1])
        elif ituple[0] == MIN_VALIDATOR:
            param = __validate_min(param_key, param, ituple[1])
        elif ituple[0] == MAX_VALIDATOR:
            param = __validate_max(param_key, param, ituple[1])
        elif ituple[0] == REGEX_VALIDATOR:
            param = __validate_regex(param_key, param, ituple[1])
        elif ituple[0] == VALID_VALUES_VALIDATOR:
            param = __validate_valid_values(param_key, param, ituple[1])
        elif ituple[0] == NUMERIC_STRING_VALIDATOR:
            param = __validate_numeric_string(param_key, param)


def validate_param(origin, param_key, param_tuple, required=False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if origin == REQUEST_QUERY_PARAMS:
                data = request.args
            elif origin == REQUEST_BODY:
                data = request.json
            else:
                raise InternalServerError("An internal server error occurred during param %s validation." % param_key)
            validate_param_internal(data, param_key, param_tuple, required)
            return func(*args, **kwargs)
        return update_wrapper(wrapper, func)
    return decorator


def _validate_params(origin, params_dict, data=None):
    if data is None:
        if origin == REQUEST_QUERY_PARAMS:
            data = request.args
        elif origin == REQUEST_BODY:
            data = request.json
        else:
            raise InternalServerError("An internal server error occurred during param validation.")
    for param_key, param_data in params_dict.iteritems():
        if param_data.get("derivated", False):
            if type(param_data) == dict:
                if param_data.get("many", False):
                    for i_param_data in data.get(param_key, []):
                        _validate_params(origin, params_dict=param_data.get("fields", {}), data=i_param_data)
                else:
                    _validate_params(origin, params_dict=param_data.get("fields", {}), data=data.get(param_key))
        else:
            required = param_data.get("required", False)
            param_tuple = param_data.get("validation_tuple", [])
            validate_param_internal(data, param_key, param_tuple, required)