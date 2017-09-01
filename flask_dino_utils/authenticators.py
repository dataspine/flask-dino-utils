from werkzeug.exceptions import Unauthorized, Forbidden, BadRequest
from exceptions import AttributeError
import operator


class Authenticator:
    USER_OBJECT = None
    USERNAME_ATTR = "username"
    PASSWORD_ATTR = "password"
    SUPER_ROLE_ATTR = "role.is_super_role"
    PERMISSIONS_ATTR = "role.permissions"
    KEY_PERMISSION_ATTR = "user_permission_arn"

    def __init__(self):
        pass

    def __check_user_permissions(self, username, password, permission):
        user = self.USER_OBJECT.query.filter(getattr(self.USER_OBJECT, self.USERNAME_ATTR) == username)\
        .filter(getattr(self.USER_OBJECT, self.PASSWORD_ATTR) == password).first()
        if user is None:
            raise Unauthorized("The username might not exist or password is incorrect")
        if self.SUPER_ROLE_ATTR is not None:
            try:
                is_superuser = operator.attrgetter(self.SUPER_ROLE_ATTR)(user)
                if is_superuser:
                    return user
            except AttributeError:
                raise BadRequest("Internal error defining %s attribute. Not found in object." % self.SUPER_ROLE_ATTR)
        if self.PERMISSIONS_ATTR is not None and permission is not None:
            permissions = []
            try:
                permissions = operator.attrgetter(self.PERMISSIONS_ATTR)(user)
            except AttributeError:
                raise BadRequest("Internal error defining %s attribute. Not found in object." % self.PERMISSIONS_ATTR)
            try:
                permission_keys = [getattr(i_permission, self.KEY_PERMISSION_ATTR) for i_permission in permissions]
                if permission in permission_keys:
                    return user
                else:
                    raise Forbidden("User %s does not have permissions to execute %s" % (username, permission))
            except AttributeError:
                raise BadRequest("Internal error defining %s attribute. Not found in object."
                                 % self.KEY_PERMISSION_ATTR)
        return user

    def basic_auth(self, authorization, permission):
        if authorization is None or authorization.username is None or authorization.password is None:
            raise Unauthorized("There are missing authorization parameters. Please send user and password "
                               "in Authorization header.")
        user = self.__check_user_permissions(authorization.username, authorization.password, permission)
        return user
