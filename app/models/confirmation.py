# from uuid import uuid4
from time import time
import mongoengine as me


# CONFIRMATION_EXPIRATION_DELTA = 1800

class ConfirmationModel(me.EmbeddedDocument):
    uid = me.StringField()
    expire_at = me.IntField()
    confirmed = me.BooleanField()
    expired = me.BooleanField()

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     self.uid = uuid4().hex
    #     self.expire_at = int(time()) + CONFIRMATION_EXPIRATION_DELTA
    #     self.confirmed = False
    #     self.expired = False

    @classmethod
    def find_by_id(cls, id: str) -> 'ConfirmationModel':
        return cls.objects(uid=id)

    def force_to_expire(self) -> None:
        if not self.expired:
            self.expired = True
    
