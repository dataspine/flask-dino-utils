import ast
from werkzeug.exceptions import BadRequest


FILTER_SEPARATOR = '$'
FILTER_VALUES_SEPARATOR = ';'


def _filter_query(model_class, query, filter_string):
    if filter_string is None:
        return query
    # model_class = type(query)  # returns the query's Model
    raw_filters = filter_string.split(FILTER_SEPARATOR)
    for raw in raw_filters:
        try:
            filter_key, filter_operator, filter_value = raw.split(FILTER_VALUES_SEPARATOR, 3)
        except ValueError:
            raise BadRequest('The filter string %s is not a valid filter format' % filter_string)
        column = getattr(model_class, filter_key, None)
        if not column:
            raise BadRequest('The filter_key %s is not a valid column' % filter_key)
        if filter_operator == 'in':
            filter_expression = column.in_(filter_value.split(','))
        else:
            try:
                attr = filter(
                    lambda e: hasattr(column, e % filter_operator),
                    ['%s', '%s_', '__%s__']
                )[0] % filter_operator
            except IndexError:
                raise BadRequest('Invalid filter operator: %s' % filter_operator)
            if filter_value == 'null':
                filter_value = None
            filter_expression = getattr(column, attr)(filter_value)
        query = query.filter(filter_expression)
    return query
