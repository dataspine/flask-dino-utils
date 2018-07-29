from flask_classy import FlaskView
from flask import request, jsonify
from validators import TYPE_VALIDATOR
from marshmallow import *
from pagination import _validate_pagination_parameters, paginated_response
from sorting import _validate_sorting_parameters, sort
from filtering import _filter_query
from validators import _validate_params, REQUEST_BODY
from werkzeug.exceptions import BadRequest, NotFound

CREATE_NEW_OBJECT = "CREATE_NEW"
ASSOCIATE_EXISTING_OBJECT = "ASSOCIATE_EXISTING"


class FlaskImprovedView(FlaskView):
    route_base = "/"
    id_name = "id"
    view_schema = Schema()
    active_field = "active"
    view_model = None
    db_engine = None
    extra_filters = None
    body_validation = {
        "sample_attribute": {
            "required": True,
            "validation_tuple": [(TYPE_VALIDATOR, unicode)]
        },
        "derivated_attribute": {
            "derivated": True,
            "object_type": None,
            "id_name": "id_derivated",
            "create_behavior": CREATE_NEW_OBJECT,
            "many": False,
            "fields": {
                "attribute1": {
                    "required": True,
                    "validation_tuple": [(TYPE_VALIDATOR, unicode)]
                }
            }
        }
    }
    status_codes = {
        "index": 200,
        "get": 200,
        "post": 201,
        "put": 200,
        "delete": 204
    }
    extra_response = {}

    def __process_derivated_attribute(self, derivated_data, derivated_validation, attr_name=None):
        object_type = derivated_validation.get("object_type", None)
        id_name = derivated_validation.get("id_name", None)
        create_behavior = derivated_validation.get("create_behavior", None)
        if derivated_data is None or derivated_data == [] or derivated_data == {}:
            if derivated_validation.get("required", False):
                raise BadRequest("A missing required attribute is causing the request to fail.")
            else:
                return [] if derivated_validation.get("many", False) else derivated_data
        if derivated_validation.get("many", True) and type(derivated_data) == list:
            new_list_objects = list()
            for items_objects in derivated_data:
                new_object = self.__process_derivated_attribute(items_objects, derivated_validation)
                new_list_objects.append(new_object)
            return new_list_objects
        else:
            if create_behavior == CREATE_NEW_OBJECT:
                new_object = object_type()
                for key, value in derivated_validation.get("fields", {}).iteritems():
                    if value.get("derivated", False):
                        setattr(new_object, key, self.__process_derivated_attribute(derivated_data.get(key),
                                                                                    value))
                    else:
                        setattr(new_object, key, derivated_data.get(key))
                return new_object
            elif create_behavior == ASSOCIATE_EXISTING_OBJECT:
                existing_object = object_type.query.filter(getattr(object_type, id_name) == derivated_data.get(id_name, None)).first()
                if existing_object is None:
                    raise NotFound("Object of type %s with id %s not found in server. Try changing the id value."
                                   % (object_type, derivated_data.get(id_name, None)))
                return existing_object
        return None

    def index(self):
        _validate_sorting_parameters(request.args, self.view_model)
        _validate_pagination_parameters(request.args)
        result = self.view_model.query
        if request.args.get("filter", None) is None:
            actual_filter = self.extra_filters
        else:
            actual_filter = request.args.get("filter", None)
            if self.extra_filters is not None:
                actual_filter += "$" + self.extra_filters
        result = _filter_query(self.view_model, result, actual_filter)
        sorted_result = sort(request.args, result)
        return paginated_response(request.args, sorted_result, type(self.view_schema))

    def get(self, id):
        result = self.view_model.query.get_or_404(int(id))
        response_data = jsonify(response=self.view_schema.dump(result).data)
        if self.extra_response != None and self.extra_response != {}:
            response_data = {"response": self.view_schema.dump(result).data}
            response_data.update(self.extra_response)
        else:
            response_data = self.view_schema.dump(result).data
        return jsonify(response_data), self.status_codes.get("get", 200)

    def post(self):
        _validate_params(REQUEST_BODY, self.body_validation)
        data = request.json
        new_object = self.view_model()
        for key, value in data.iteritems():
            if type(value) in [list, dict]:
                setattr(new_object, key, self.__process_derivated_attribute(value, self.body_validation.get(key)))
            elif key != self.id_name and key in self.view_model.__table__.columns.keys():
                setattr(new_object, key, value)
        self.db_engine.session.add(new_object)
        try:
            self.db_engine.session.commit()
        except:
            self.db_engine.session.rollback()
            raise
        if self.extra_response != None and self.extra_response != {}:
            response_data = {"response": self.view_schema.dump(new_object).data}
            response_data.update(self.extra_response)
        else:
            response_data = self.view_schema.dump(new_object).data
        return jsonify(response_data), self.status_codes.get("post", 201)

    def put(self, id):
        _validate_params(REQUEST_BODY, self.body_validation)
        merged_object = self.view_model.query.get_or_404(int(id))
        data = request.json
        for key, value in data.iteritems():
            if type(value) in [list, dict]:
                setattr(merged_object, key, self.__process_derivated_attribute(value, self.body_validation.get(key)))
            elif key != self.id_name and key in self.view_model.__table__.columns.keys():
                setattr(merged_object, key, value)
        self.db_engine.session.merge(merged_object)
        try:
            self.db_engine.session.commit()
        except:
            self.db_engine.session.rollback()
            raise
        if self.extra_response != None and self.extra_response != {}:
            response_data = {"response": self.view_schema.dump(merged_object).data}
            response_data.update(self.extra_response)
        else:
            response_data = self.view_schema.dump(merged_object).data
        return jsonify(response_data), self.status_codes.get("put", 200)

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
        response_data = {"message": "Successfully deleted item"}
        if self.extra_response != None and self.extra_response != {}:
            response_data.update(self.extra_response)
        return jsonify(response_data), self.status_codes.get("delete", 204)

