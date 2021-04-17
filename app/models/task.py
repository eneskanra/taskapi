from flask import request, url_for
from requests import Response
from libs.mailgun import Mailgun
from models.user import UserModel
from models.comment import CommentModel
import mongoengine as me


class TaskModel(me.EmbeddedDocument):
    title = me.StringField(required=True)
    content = me.StringField(required=True)
    startdate = me.DateTimeField()
    enddate =me.DateTimeField()
    createdate = me.DateTimeField()
    completedate = me.DateTimeField()
    status = me.StringField(choices=['Boşta', 'Alındı', 'Başladı', 'Kontrolde', 'Tamamlandı'])
    owner = me.ReferenceField(UserModel)
    assigned = me.ReferenceField(UserModel)
    comment = me.ListField(me.EmbeddedDocumentField(CommentModel))

    @classmethod
    def find_by_title(cls, title: str) -> 'TaskModel':
        return cls.objects(title=title).first()

    @classmethod
    def find_by_id(cls, id: str) -> 'TaskModel':
        return cls.objects(_id=id).first()
