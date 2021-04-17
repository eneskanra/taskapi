import marshmallow_mongoengine as ma
from marshmallow.fields import Nested 
from models.project import ProjectModel
from schemas.user import UserSchema


class ProjectSchema(ma.ModelSchema):
    class Meta:
        model = ProjectModel
    
    owner = Nested(UserSchema, only=["username"])
    authorized = Nested(UserSchema, only=["username"], many=True)
    # task = Nested("TaskSchema", many=True)