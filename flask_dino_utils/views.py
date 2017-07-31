from flask_classy import FlaskView
from flask import request, jsonify
from validators import TYPE_VALIDATOR
from marshmallow import *
from pagination import _validate_pagination_parameters, paginated_response
from sorting import _validate_sorting_parameters, sort
from filtering import _filter_query
from validators import _validate_params
import ast

class FlaskImprovedView(FlaskView):
    route_base = "/"
    id_name = "id"
    view_schema = Schema()
    view_model = None
    body_validation = {
        "attribute1": {
            "required": True,
            "validation_tuple": [(TYPE_VALIDATOR, unicode)]
        }
    }
    index_filter_validation = {
        "attribute1": {
            "required": False,
            "validation_tuple": [(TYPE_VALIDATOR, unicode)]
        }
    }

    def index(self):
        #_validate_params(self.index_filter_validation)
        _validate_sorting_parameters(request.args, self.view_model)
        _validate_pagination_parameters(request.args)
        result = self.view_model.query
        result = _filter_query(self.view_model, result, request.args.get("filter", None))
        sorted_result = sort(request.args, result)
        return paginated_response(request.args, sorted_result, type(self.view_schema))

    def get(self, id):
        result = self.view_model.query.get_or_404(int(id))
        return jsonify(self.view_schema.dump(result).data)

    def post(self):
        pass

    def put(self, id):
        pass

    def delete(self, id):
        pass
