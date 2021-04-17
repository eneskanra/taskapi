from flask import request, url_for
from requests import Response
from libs.mailgun import Mailgun
from models.user import UserModel
from models.task import TaskModel
import mongoengine as me


class ProjectModel(me.Document):
    name = me.StringField(required=True)
    status = me.StringField(required=True, choices=['Active', 'Archived'], default="Active")
    createdate = me.DateTimeField()
    owner = me.ReferenceField(UserModel)
    authorized = me.ListField(me.ReferenceField(UserModel))
    task = me.ListField(me.EmbeddedDocumentField(TaskModel))

    @classmethod
    def find_by_name(cls, name: str) -> 'ProjectModel':
        return cls.objects(name=name).first()
    
    @classmethod
    def find_by_owner(cls, name: str) -> 'ProjectModel':
        return cls.objects(owner=name).first()

    @classmethod
    def find_by_id(cls, id: int) -> 'ProjectModel':
        return cls.objects(_id=id).first()

