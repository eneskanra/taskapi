from marshmallow import pre_dump
from models.user import UserModel
import marshmallow_mongoengine as ma


class UserSchema(ma.ModelSchema):
    class Meta:
        model = UserModel
        model_fields_kwargs = {
            'password': {'load_only': True}
        }
       
# class UserSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = UserModel
#         load_only = ('password',)
#         dump_only = ('id', 'confirmation')
#         include_relationships = True
#         load_instance = True

#     @pre_dump(pass_many=False)
#     def _pre_dump(self, user: UserModel, **kwargs):
#         user.confirmation = [user.most_recent_confirmation]
#         return user