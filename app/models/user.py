from flask import request, url_for
from requests import Response
from libs.mailgun import Mailgun
from models.confirmation import ConfirmationModel
import mongoengine as me


class UserModel(me.Document):
    username = me.StringField(required=True)
    password = me.StringField(required=True)
    email = me.StringField(required=True)
    confirmation = me.ListField(me.EmbeddedDocumentField(ConfirmationModel))

    def __repr__(self):
        return self.username
        
    def __str__(self):
        return self.username

    @property
    def most_recent_confirmation(self) -> 'ConfirmationModel':
        return self.confirmation[-1]

    @classmethod
    def find_by_username(cls, username: str) -> 'UserModel':
        return cls.objects(username=username).first()
    
    @classmethod
    def find_by_email(cls, email: str) -> 'UserModel':
        return cls.objects(email=email).first()

    @classmethod
    def find_by_id(cls, _id: int) -> 'UserModel':
        return cls.objects(_id=_id).first()

    def send_confirmation_email(self) -> Response:
        link = request.url_root[:-1] + url_for(
            'confirmation',
            username=self.username,
            confirmation_id=self.most_recent_confirmation.uid
        )
        subject=  "Registration Confirmation"
        text = f"Please click the link to confirm your registration: {link}"
        html = f'<html>Please click the link to confirm your registration: <a href="{link}">{link}</a></html>'
        return Mailgun.send_email([self.email], subject, text, html)

    def save_to_db(self) -> None:
        self.save()
    
    def delete_from_db(self) -> None:
        self.delete()