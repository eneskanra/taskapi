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
from schemas.task import TaskSchema
from schemas.comment import CommentSchema
from models.user import UserModel
from models.project import ProjectModel
from models.task import TaskModel
from models.comment import CommentModel
from blacklist import BLACKLIST
from libs.mailgun import MailgunException


user_schema = UserSchema()

comment_schema = CommentSchema()

comment_list_schema = CommentSchema(many=True)


class Comment(Resource):
    @classmethod
    @jwt_required()
    def post(cls, project: str, task: str):
        project = ProjectModel.find_by_name(project)
        if not project:
            return {'message': gettext("project_not_found").format(project)}, 400
        current_user = get_jwt_identity()
        user = UserModel.find_by_username(current_user)
        if user not in project.authorized:
            return {'message': gettext("project_not_authorized")}, 401
        
        for taskItem in project.task:
            if taskItem.title == task:
                comment_json = request.get_json()
                comment = comment_schema.load(comment_json)
                comment['user'] = user
                comment['id'] = uuid4().hex
                comment['date'] = datetime.now()
                print(comment.to_json())
                # taskItem.comment.append(comment)
                ProjectModel.objects.filter(task__title=task).update(push__task__S__comment=comment)
        # project.save()
        return comment_schema.dump(comment), 201  


class CommentList(Resource):
    @classmethod
    @jwt_required()
    def get(cls, project: str, task: str):
        project = ProjectModel.find_by_name(project)
        if not project:
            return {'message': gettext("project_not_found").format(project)}, 400
        current_user = get_jwt_identity()
        user = UserModel.find_by_username(current_user)
        if user not in project.authorized:
            return {'message': gettext("project_not_authorized")}, 401
        for taskItem in project.task:
            if taskItem.title == task:
                return {'comment': comment_list_schema.dump(taskItem.comment)}
                
        



