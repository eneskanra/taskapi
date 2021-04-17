import marshmallow_mongoengine as ma
from marshmallow.fields import Nested 
from models.task import TaskModel
from schemas.user import UserSchema
from schemas.comment import CommentSchema

class TaskSchema(ma.ModelSchema):
    class Meta:
        model = TaskModel
    
    owner = Nested(UserSchema, only=["username"])
    assigned = Nested(UserSchema, only=["username"])
    comment = Nested(CommentSchema, many=True)