import marshmallow_mongoengine as ma
from marshmallow.fields import Nested 
from models.comment import CommentModel
from schemas.user import UserSchema

class CommentSchema(ma.ModelSchema):
    class Meta:
        model = CommentModel
    
    user = Nested(UserSchema, only=["username"])