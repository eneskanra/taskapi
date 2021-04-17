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
from models.user import UserModel
from models.project import ProjectModel
from models.task import TaskModel
from blacklist import BLACKLIST
from libs.mailgun import MailgunException


user_schema = UserSchema()

project_schema = ProjectSchema()

task_schema = TaskSchema()

task_list_schema = TaskSchema(many=True)


class Task(Resource):
    @classmethod
    @jwt_required()
    def get(cls, project: str, title: str):
        project = ProjectModel.find_by_name(project)
        if not project:
            return {'message': gettext("project_not_found").format(project)}, 400
        current_user = get_jwt_identity()
        user = UserModel.find_by_username(current_user)
        if user not in project.authorized:
            return {'message': gettext("project_not_authorized")}, 401
        for taskItem in project.task:
            if taskItem.title == title:
                return task_schema.dump(taskItem), 200
        return {'message': gettext("task_not_found")}, 404
        

    @classmethod
    @jwt_required()
    def post(cls, project: str, title: str):
        project = ProjectModel.find_by_name(project)
        if not project:
            return {'message': gettext("project_not_found").format(project)}, 400
        current_user = get_jwt_identity()
        user = UserModel.find_by_username(current_user)
        if user not in project.authorized:
            return {'message': gettext("project_not_authorized")}, 401
        for taskItem in project.task:
            if taskItem.title == title:
                return {'message': gettext("task_name_exists").format(title)}, 400
        task_json = request.get_json()
        task_json['title'] = title
        if "assigned" in task_json:
            user_assg = UserModel.find_by_username(task_json['assigned'])
            task_json.pop("assigned")
        else:
            user_assg = None
        task = task_schema.load(task_json)
        task['createdate'] = datetime.now()
        task['owner'] = user
        task['status'] = "Boşta"
        if user_assg:
            task['assigned'] = user_assg

        print(task.to_json())
        try:
            project.task.append(task)
            project.save()
        except:
            return {"message": gettext("task_error_creating")}, 500

        return task_schema.dump(task), 201
    
    @classmethod
    @jwt_required()
    def put(cls, project: str, title: str):
        project = ProjectModel.find_by_name(project)
        if not project:
            return {'message': gettext("project_not_found").format(project)}, 400
        current_user = get_jwt_identity()
        user = UserModel.find_by_username(current_user)
        if user not in project.authorized:
            return {'message': gettext("project_not_authorized")}, 401
        for taskItem in project.task:
            if taskItem.title == title:
                taskDict = task_schema.dump(taskItem)
                taskDict.pop("owner", None)
                taskDict.pop("assigned", None)
                task_json = request.get_json()
                print(task_json)
                task_json["title"] = title
                if "assigned" in task_json:
                    user_assg = UserModel.find_by_username(task_json['assigned'])
                    task_json.pop("assigned", None)
                else:
                    user_assg = None
                taskDict.update(task_json)
                print(taskDict)
                task = task_schema.load(taskDict)
                task['owner'] = user
                if user_assg:
                    task['assigned'] = user_assg
                print(task.to_json())
                project.update(pull__task__title=title)
                project.reload()
                # ProjectModel.objects.filter(task__title=task).update(push__task=task)
                
                
                project.task.append(task)
                project.save()
                return {"message": "success"}, 500
                # try:
                #     project.task.append(task)
                #     project.save()
                # except:
                #     return {"message": gettext("task_error_creating")}, 500
                # return task_schema.dump(task), 201 
        return {'message': gettext("task_not_found")}, 400
    @classmethod
    @jwt_required()
    def delete(cls, project: str, title: str):
        project = ProjectModel.find_by_name(project)
        if not project:
            return {'message': gettext("project_not_found").format(project)}, 400
        current_user = get_jwt_identity()
        user = UserModel.find_by_username(current_user)
        if user not in project.authorized:
            return {'message': gettext("project_not_authorized")}, 401
        for taskItem in project.task:
            if taskItem.title == title:
                project.update(pull__task__title=title)
                return {'message': gettext("task_deleted")}, 200
        return {'message': gettext("task_not_found")}, 404
        
        

class TaskList(Resource):
    @classmethod
    @jwt_required()
    def get(cls, project: str):
        project = ProjectModel.find_by_name(project)
        if not project:
            return {'message': gettext("project_not_found").format(project)}, 400
        current_user = get_jwt_identity()
        user = UserModel.find_by_username(current_user)
        if user not in project.authorized:
            return {'message': gettext("project_not_authorized")}, 401
        return {'task': task_list_schema.dump(project.task)}, 200



