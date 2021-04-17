import os
from dotenv import load_dotenv
load_dotenv('.env', verbose=True)

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from marshmallow import ValidationError
from flask_mongoengine import MongoEngine
db = MongoEngine()
from ma import ma
from resources.user import (
    UserRegister, 
    User, 
    UserLogin, 
    UserLogout,
    TokenRefresh,
)
from resources.confirmation import Confirmation, ConfirmationByUser
from resources.project import Project, ProjectList
from resources.task import Task, TaskList
from resources.comment import Comment, CommentList
from blacklist import BLACKLIST


app = Flask(__name__)

app.config.from_object("default_config")
app.config.from_envvar("APPLICATION_SETTINGS")
app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_DATABASE']
}

api = Api(app)
db.init_app(app)
ma.init_app(app)

jwt = JWTManager(app)


# @app.before_first_request
# def create_tables():
#     db.create_all()

@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400


@jwt.additional_claims_loader
def add_claims_to_jwt(identity):  # Remember identity is what we define when creating the access token
    if identity == 1:   # instead of hard-coding, we should read from a config file or database to get a list of admins instead
        return {'is_admin': True}
    return {'is_admin': False}

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(decrypted_header, decrypted_body):
    return decrypted_body['jti'] in BLACKLIST

@jwt.expired_token_loader
def expired_token_callback(decrypted_header, decrypted_body):
    return jsonify({
        'description': 'The token has expired.',
        'error': 'token_expired'
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):  # we have to keep the argument here, since it's passed in by the caller internally
    return jsonify({
        'description': 'Signature verification failed.',
        'error': 'invalid_token'
    }), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'description': 'Request does not contain an access token.',
        'error': 'authorization_required'
    }), 401


@jwt.needs_fresh_token_loader
def token_not_fresh_callback(decrypted_header, decrypted_body):
    return jsonify({
        'description': 'The token is not fresh.',
        'error': 'fresh_token_required'
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback(decrypted_header, decrypted_body):
    return jsonify({
        'description': 'The token has been revoked.',
        'error': 'token_revoked'
    }), 401


api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<string:username>')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(Confirmation, '/user_confirmation/<string:username>/<string:confirmation_id>')
api.add_resource(ConfirmationByUser, '/confirmation/user/<string:username>')
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(Project, '/project/<string:name>')
api.add_resource(ProjectList, '/projects')
api.add_resource(Task, '/task/<string:project>/<string:title>')
api.add_resource(TaskList, '/tasks/<string:project>')
api.add_resource(Comment, '/comment/<string:project>/<string:task>')
api.add_resource(CommentList, '/comments/<string:project>/<string:task>')

if __name__ == '__main__':
    app.run(port=5000, debug=True)