import traceback
from uuid import uuid4
from time import time
from flask_restful import Resource
from flask import request
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity,
    get_jwt
)
from marshmallow import ValidationError
from libs.strings import gettext
from schemas.user import UserSchema
from models.user import UserModel
from blacklist import BLACKLIST
from libs.mailgun import MailgunException
from models.confirmation import ConfirmationModel

user_schema = UserSchema()

CONFIRMATION_EXPIRATION_DELTA = 1800

class UserRegister(Resource):
    @classmethod
    def post(cls):
        user_json = request.get_json()
        user = user_schema.load(user_json)
        print(user)
        if UserModel.find_by_username(user.username):
            return {"message": gettext("user_username_exists")}, 400

        if UserModel.find_by_email(user.email):
            return {"message": gettext("user_email_exists")}, 400

        try:
            expire_at = int(time()) + CONFIRMATION_EXPIRATION_DELTA
            confirmation = ConfirmationModel(
                uid=uuid4().hex,
                expire_at=expire_at,
                confirmed=True, # User confirmation geçici olarak devre dışı bırakıldı
                expired=False
            )
            print(confirmation)
            print(confirmation.to_json())
            user.confirmation.append(confirmation)
            print(user)
            print(user.to_json())
            user.save_to_db()
            # user.send_confirmation_email() # User confirmation geçici olarak devre dışı bırakıldı
            return {"message": gettext("user_registered")}, 201
        except MailgunException as e:
            user.delete_from_db()
            return {"message": str(e)}, 500
        except:
            traceback.print_exc()
            user.delete_from_db()
            return {"message": gettext("user_error_creating")}, 500


class User(Resource):
    """
    This resource can be useful when testing our Flask app.
    """
    @classmethod
    def get(cls, username: str):
        user = UserModel.find_by_username(username)
        if not user:
            return {'message': gettext("user_not_found")}, 404
        return user_schema.dump(user), 200

    @classmethod
    def delete(cls, username: str):
        user = UserModel.find_by_username(username)
        if not user:
            return {'message': gettext("user_not_found")}, 404
        user.delete_from_db()
        return {'message': gettext("user_deleted")}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        user_json = request.get_json()
        user_data = user_schema.load(user_json, partial=('email',))
        user = UserModel.find_by_username(user_data.username)

        if user and safe_str_cmp(user.password, user_data.password):
            confirmation = user.most_recent_confirmation
            if confirmation and confirmation.confirmed:
                access_token = create_access_token(identity=user.username, fresh=True) 
                refresh_token = create_refresh_token(user.username)
                return {
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }, 200
            return {'message': gettext("user_not_confirmed").format(user.username)}, 400

        return {"message": gettext("user_invalid_credentials")}, 401

class UserLogout(Resource):
    @classmethod
    @jwt_required()
    def post(cls):
        jti = get_jwt()['jti']
        BLACKLIST.add(jti)
        return {'message': gettext("user_logged_out")}, 200

class TokenRefresh(Resource):
    @classmethod
    @jwt_required(refresh=True)
    def post(cls):
        """
        Get a new access token without requiring username and password—only the 'refresh token'
        provided in the /login endpoint.
        Note that refreshed access tokens have a `fresh=False`, which means that the user may have not
        given us their username and password for potentially a long time (if the token has been
        refreshed many times over).
        """
        current_user = get_jwt_identity()
        print(current_user)
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200

