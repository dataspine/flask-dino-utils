from flask_classy import FlaskView
from flask import request, jsonify
from validators import TYPE_VALIDATOR
from marshmallow import *
from pagination import _validate_pagination_parameters, paginated_response
from sorting import _validate_sorting_parameters, sort
from filtering import _filter_query
from validators import _validate_params, REQUEST_BODY


class FlaskImprovedView(FlaskView):
    route_base = "/"
    id_name = "id"
    view_schema = Schema()
    active_field = "active"
    view_model = None
    db_engine = None
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
        _validate_params(REQUEST_BODY, self.body_validation)
        data = request.json
        new_object = self.view_model()
        for key, value in data.iteritems():
            if key != self.id_name and key in self.view_model.__table__.columns.keys():
                setattr(new_object, key, value)
        self.db_engine.session.add(new_object)
        try:
            self.db_engine.session.commit()
        except:
            self.db_engine.session.rollback()
            raise
        return jsonify(self.view_schema.dump(new_object).data), 201

    def put(self, id):
        _validate_params(REQUEST_BODY, self.body_validation)
        merged_object = self.view_model.query.get_or_404(int(id))
        data = request.json
        for key, value in data.iteritems():
            if key != self.id_name and key in self.view_model.__table__.columns.keys():
                setattr(merged_object, key, value)
        self.db_engine.session.merge(merged_object)
        try:
            self.db_engine.session.commit()
        except:
            self.db_engine.session.rollback()
            raise
        return jsonify(self.view_schema.dump(merged_object).data), 200

    def delete(self, id):
        deleted_object = self.view_model.query.get_or_404(int(id))
        if self.active_field is None or self.active_field not in self.view_model.__table__.columns.keys():
            self.db_engine.session.delete(deleted_object)
        else:
            setattr(deleted_object, self.active_field, False)
            self.db_engine.session.merge(deleted_object)
        try:
            self.db_engine.session.commit()
        except:
            self.db_engine.session.rollback()
            raise
        return jsonify({"message": "Successfully deleted item"}), 204

