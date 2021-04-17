import traceback
from uuid import uuid4
from time import time
from datetime import datetime
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
from schemas.project import ProjectSchema
from models.user import UserModel
from models.project import ProjectModel
from blacklist import BLACKLIST
from libs.mailgun import MailgunException


user_schema = UserSchema()

project_schema = ProjectSchema()

project_list_schema = ProjectSchema(many=True)


class Project(Resource):
    @classmethod
    @jwt_required()
    def get(cls, name: str):
        project = ProjectModel.find_by_name(name)
        if not project:
            return {'message': gettext("project_not_found")}, 404
        current_user = get_jwt_identity()
        user = UserModel.find_by_username(current_user)
        if user not in project.authorized:
            return {'message': gettext("project_not_authorized")}, 401
        return project_schema.dump(project), 200

    @classmethod
    @jwt_required()
    def post(cls, name: str):
        if ProjectModel.find_by_name(name):
            return {'message': gettext("project_name_exists").format(name)}, 400
        current_user = get_jwt_identity()
        user = UserModel.find_by_username(current_user)
        print(user.to_json())
        project_json = {}
        project_json['name'] = name
        project = project_schema.load(project_json)
        project['createdate'] = datetime.now()
        project['owner'] = user
        project['authorized'] = [user]
        print(project.to_json())
        try:
            project.save()
        except:
            return {"message": gettext("project_error_creating")}, 500

        return project_schema.dump(project), 201
    
    @classmethod
    @jwt_required()
    def put(cls, name: str):
        project_json = request.get_json()
        project = ProjectModel.find_by_name(name)
        current_user = get_jwt_identity()
        user = UserModel.find_by_username(current_user)
        if user not in project.authorized:
            return {'message': gettext("project_not_authorized")}, 401
        if project:
            project.status = project_json['status']
        else:
            project_json['name'] = name
            project = project_schema.load(project_json)
        try:
            project.save()
        except:
            return {"message": gettext("project_error_creating")}, 500

        return project_schema.dump(project), 200

    @classmethod
    @jwt_required()
    def delete(cls, name: str):
        project = ProjectModel.find_by_name(name)
        if not project:
            return {'message': gettext("project_not_found")}, 404
        current_user = get_jwt_identity()
        user = UserModel.find_by_username(current_user)
        if user not in project.authorized:
            return {'message': gettext("project_not_authorized")}, 401
        project.delete()
        return {'message': gettext("project_deleted")}, 200

class ProjectList(Resource):
    @classmethod
    @jwt_required()
    def get(cls):
        current_user = get_jwt_identity()
        user = UserModel.find_by_username(current_user)
        
        return {'projects': project_list_schema.dump(ProjectModel.objects.filter(authorized=user))}

