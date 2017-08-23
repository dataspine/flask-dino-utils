[![Build Status](https://travis-ci.org/dinocloud/flask-dino-utils.svg?branch=master)](https://travis-ci.org/dinocloud/flask-dino-utils)
[![PyPI version](https://badge.fury.io/py/flask_dino_utils.svg)](https://badge.fury.io/py/flask_dino_utils)

# flask-dino-utils - A toolbox to make API development easier.
So, you are already a trained python developer and you love building projects using Flask, but there are some processes that you already do like a robot, like building the logic to paginate your api. How cool would it be if those things could be already wrapped up as possible? Well, search no more. Flask-Dino-Utils is here to help you build robust flask apis in no time. 

## Assumptions

In order to use this library we make some assumptions regarding your project.

* You're using the following frameworks: `flask-classy`, `flask-sqlalchemy` and `marshmallow`.
* Each of your objects has an autoincrement id. (With any name).
* Your class attributes are exactly the same as your table columns.

## Our Big Baby: The FlaskImprovedView

So, you love Flask-Classy and basically you use `FlaskView` as your superclass in any view you create. Well, say no more. You're not going to use that class anymore. Now, you will start using FlaskImprovedView which adds the following functionality:

* In `GET /`: Adds pagination, sorting, and filtering your objects. For *pagination* you can use `per_page` and `page` parameters. For sorting you can use `sort_field` and `sort_dir` (asc and desc) parameters. And for filtering we have a custom and easy-to-use syntax to add *any* filter you need. See Flask-Dino Filter syntax for more information.
* In `GET /<id>`: Does the logic needed to return the object.
* In `POST /`: Creates an object validating the json input using the `body_validation` attribute. It creates and returns the object.
* In `PUT /<id>`: Modifies an existing object giving the id sent by parameter.
* In `DELETE /<id>`: Delete (or alter an active field) an object.

### FlaskImprovedView attributes.

Here's an very quick example of an implementation of a child view:

```
class UserPositionView(FlaskImprovedView):
    route_base = "/user_positions" # Endpoint
    id_name = "id_user_position" # The id field name
    view_schema = UserPositionSchema() # The marshmallow schema object
    view_model = UserPosition # The SQLAlchemy Model class
    db_engine = db # The database engine to make the operations
    active_field = "active" # The active field if you do not want to delete any database registry but to alter a boolean value.
    body_validation = { # A set of definitions in the params validation process.
        "user_position_description": {
            "required": True,
            "validation_tuple": [(TYPE_VALIDATOR, unicode)]
        },
        "company": {
            "derivated": True,
            "object_type": Company,
            "id_name": "id_company",
            "create_behavior": ASSOCIATE_EXISTING_OBJECT,
            "many": False,
            "fields": {
                "id_company": {
                    "required": True,
                    "validation_tuple": [(TYPE_VALIDATION, int)]
                }
            }
        }
    }
```

* `route_base` : The `FlaskView` route attribute. Nothing new.
* `id_name`: The name of the id attribute in order to perform some logic in POST and PUT commands.
* `view_schema`: The marshmallow serializer object instantiated.
* `view_model`: The SQLAlchemy class to perform queries over orm model.
* `body_validation`: The parameters validation in payload body in an object creation/modification. (See Payload validation for more info).
* `db_engine`: The database engine to operate. Usually it's a SqlAlchemy initiated engine.
* `active_field`: The name of the active attribute if you do not want to delete any table registry but to alter a boolean value.

## The derivated attributes
As any object-oriented programming world, we will have relationships between objects that will end up in json (or list) inside our body.
This object, obviously, requires a validation also. You may have a *single-object* or a *list of objects* that needs to be *created* or *associated* among with the main object.
The parameters for the `body_validation` attribute for derivated objects are:
* `derivated`: `True` specify that the attribute is a derivated one. Otherwise will not be taken by the validation algorithms.
* `object_type`: Same as the view, we need to know the object type of your derivated param.
* `id_name`: We need to know which of the fields is the id attribute.
* `create_behavior`: This is an important one. You may define: 
    * `ASSOCIATE_EXISTING_OBJECT`: In this case, whether is a `POST` or a `PUT` method, the method will look for the id of the object sent and will be associating it to our main object. It will *not* create a new one.
    * `CREATE_NEW_OBJECT: In this case, a new object (or objects) will be created among with our object creation.
* `many`: If it is `True` the view will expect a list of derivated objects. If it is `False` will expect only one.
* `fields`: In this case, we will be defining the validation fields inside this key.


## Individual decorators for custom endpoints.
Okay, so you're saying: "Awesome! But my api is much more complex than 5 CRUD methods. I need more power man.". No problem! We added decorators for each individual operation so you can add it to any endpoint and customize your logic as well. Remember, we *only* want you to take care of your code and not repetitive and boring stuff.

### Pagination

In order to paginate your response, you shall do two things:

1. (Optional) Add the `@paginable()` decorator to your response. This will validate the pagination parameters.
2. Use the `paginated_response(args, data, schema_class)` to paginate your SqlAlchemy query and get the result. The `args` param should be your `request.args` object, the `data` is the _in progress_ sqlalchemy query with the data and the `schema_class` is your marshmallow schema definition to include in the *items* response.

*Important:* This second step will return the marshmallow serialized object ready for the response. You can not add more filters, sorting, etc. after this. You shall call `paginated_response` at the end of your logic.

### Sorting
`
To sort your response, you shall do two things:

1. (Optional) Add the `@sortable(ObjectType)` decorator to your response method. This will validate the sorting parameters. These are `sort_dir` (asc or desc) and the `sort_field` which is the attribute/column to perform the sorting.
2. Use the `sort(args, data)` method to sort your response. The `args` param should be your `request.args` object, the `data` is the _in progress_ sqlalchemy query with the data.

### Payload validation

Now things become interesting. You can validate any param in any restful method with different conditions to forget about doing individual validation on each one. This becomes very useful if you loose lot of time validating each attribute and data when you develop your webservices. 
In our library we use the concept of *validation tuples* which consist in the *validation logic* and the *validation data*. The available validation logic and data consists in:

|Validator logic   | Description   | Data   |
|------------------|---------------|--------|
|TYPE_VALIDATOR   | Validates the type of the input param   | The object type to expect. (E.g. str, int, float)   |
|MIN_VALIDATOR   | If numeric param, validates the minimum value possible   | The minimun number to expect (included).   |
|MAX_VALIDATOR   | If numeric param, validates the maximum value possible    | The maximum number to expect (included).  |
|REGEX_VALIDATOR   | Validates that the param against a regular expression   | The regular expression to check.  |
|VALID_VALUES_VALIDATOR   | Validates against choices to use in your parameters   | A list of possible values   |
|NUMERIC_STRING_VALIDATOR   | Sometimes, you cannot send a numeric value (e.g. in a query arg). In this case you should check if the parameter is numeric-convertible.   | No data is needed here.  |

Using this logic you can validate your parameters using the `body_validation` argument for POST and PUT payloads or using the custom decorator in an api method.

#### The body_validation argument

This argument defines the validations in the payload of POST and PUT methods. The syntax is the following:

* `key`: the data to validate.
* `"required"`: if the parameter is  required or not. Default False.
* `"validation_tuple"`: The list of validation tuples to check your parameters.

An example of this:

```
body_validation = {
        "name": {
            "required": True,
            "validation_tuple": [(TYPE_VALIDATOR, unicode)]
        },
        "age": {
            "required": False,
            "validation_tuple": [(TYPE_VALIDATOR, int),(MIN_VALIDATOR, 0),(MAX_VALIDATOR, 150)]
        }
    }
```

This can be translated in individual decorators using them in any method. For example:

```
@validate_param(REQUEST_BODY_PARAMS, "name", [(TYPE_VALIDATOR, unicode)], True)
@validate_param(REQUEST_BODY_PARAMS, "age", [(TYPE_VALIDATOR, int),(MIN_VALIDATOR, 0),(MAX_VALIDATOR, 150)], False)
def post(self):
  ...
```

In this case the `REQUEST_BODY_PARAMS` defines whether to look for the param. You can use `REQUEST_QUERY_PARAMS` to check against query parameters.

### Filtering

Wow! If you read the docs and get here you're surely very impressed on how amazing restful services development can be funny without concerning on boring stuff. Well, you're right; but we have more secret weapons. In this case we're introducing the filtering option to your `GET /` requests without making you code anything (Yeh! Anything! Grab a beer and come back to Candy Crush). Not, really. The filter option is embbeded in `FlaskImprovedView` and includes every SqlAlchemy operator that you may imagine. We have a custom syntax for this, so please pay attention. Imagine that you want to filter people with name "Jack". So you developed an endpoint like this:

```
curl http://localhost:5000/api/v1/people
```

Well, if this request is using a `FlaskImprovedView` we can add the filter as the following:

```
curl http://localhost:5000/api/v1/people?filter=name;eq;Jack
```

But imagine you need people named Jack which are men, and they are between 20s and 40s. Okap, this can be done using the following request.

```
curl http://localhost:5000/api/v1/people?filter=name;eq;Jack$age;gt;20$age;lt;40
```

You can deduce in the filter syntax that the filter separator is the special character `$` and the filter logic is composed by: `<filter_key>;<filter_operator>;<filter_value>`. Filter operators can be found [here](http://docs.sqlalchemy.org/en/latest/core/sqlelement.html#sqlalchemy.sql.operators.ColumnOperators). Note: avoid using python underscores.


### The Authenticator

Under our security implementation, we have a really simple way of authenticating and authorizing users. The class `Authenticator` under `authenticators` script has all the information needed to provide a basic authentcation method.
We will assume the following object structure:

```
User 1----1 Roles 1----n Permission
```

In this case we're assuming that each user has one role associated and each role has a set of permissions associated to it. Each permission has a field regarding an unique id.
The `Authenticator` class has some predefined attributes we need to setup in orde to use it:

```python
from flask_dino_utils.authenticators import Authenticator
from models import User

authenticator = Authenticator()
authenticator.USER_OBJECT = User
authenticator.USERNAME_ATTR = "user_username" 
authenticator.PASSWORD_ATTR = "user_password"
authenticator.SUPER_ROLE_ATTR = "user_role.is_super_role"  
authenticator.PERMISSIONS_ATTR = "user_role.permissions" 
authenticator.KEY_PERMISSION_ATTR = "user_permission_arn"
```

You can see different attributes, let me explain them:

* `USER_OBJECT`:User # The object user defined on our model
* `USERNAME_ATTR`: (Required) The username attribute name to check
* `PASSWORD_ATTR`: (Required) The password attribute to check. Note: using sample comparation. The password must be encrypted from the beginning.
* `SUPER_ROLE_ATTR`: (Optional) You can have a boolean value defining that the role is super_role without concerning about permissions
* `PERMISSIONS_ATTR`: (Optional) if set, each authentication will compare against permissions
* `KEY_PERMISSION_ATTR`: (Required if defined self.PEERMISSIONS_ATTR), permissions field to compare.

After this you can add the following line to your authenticated methods:

```python
    def index(self):
        authenticator.basic_auth(authorization=request.authorization, permission="GetAllUsers")
        return super(UserView, self).index()
```

The method `basic_auth` receives the authorization data (required) and the permission uuid. If `permission` is not set, will authenticate any user and move forward.
In this case you can see that, before doing anything, first it authenticates and authorizates the user.

