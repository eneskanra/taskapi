from flask import request, url_for
from requests import Response
from libs.mailgun import Mailgun
from models.user import UserModel
import mongoengine as me


class CommentModel(me.EmbeddedDocument):
    id = me.StringField()
    content = me.StringField(required=True)
    date = me.DateTimeField()
    user = me.ReferenceField(UserModel)

    @classmethod
    def find_by_id(cls, id: int) -> 'CommentModel':
        return cls.objects(_id=id).first()
