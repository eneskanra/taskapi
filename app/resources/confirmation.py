from uuid import uuid4
from time import time
import traceback

from flask import make_response, render_template
from flask_restful import Resource

from libs.mailgun import MailgunException
from libs.strings import gettext
from models.confirmation import ConfirmationModel
from models.user import UserModel
from schemas.confirmation import ConfirmationSchema

confirmation_schema = ConfirmationSchema()

CONFIRMATION_EXPIRATION_DELTA = 1800

class Confirmation(Resource):
    @classmethod
    def get(cls, username: str, confirmation_id: str):
        """Return confirmation HTML page"""
        user = UserModel.objects(username=username).first()
        print(user.to_json())
        for item in user.confirmation:
            if item['uid'] == confirmation_id:
                confirmation = item
        
        print(confirmation.to_json())
        if not confirmation:
            return {"message": gettext("confirmation_not_found")}, 400

        if confirmation.expired:
            return {"message": gettext("confirmation_link_expired")}, 400

        if confirmation.confirmed:
            return {"message": gettext("confirmation_already_confirmed")}, 400


        UserModel.objects.filter(confirmation__uid=confirmation.uid).update(set__confirmation__S__confirmed=True)
        headers = {"Content-Type": "text/html"}
        return make_response(
            render_template("confirmation_page.html", email=user.email),
            200,
            headers
        )

class ConfirmationByUser(Resource):
    @classmethod
    def get(cls, username: str):
        """Returns confirmations for a given user. Use for testing"""
        user = UserModel.find_by_username(username)
        if not user:
            return {"message": gettext("user_not_found")}, 404

        return (
            {
                "current_time": int(time()),
                "confirmation": [
                    confirmation_schema.dump(each) 
                    for each in user.confirmation
                ],
            }, 200
        )

    @classmethod
    def post(cls, username: str):
        """Resend confirmation email"""
        user = UserModel.find_by_username(username)
        if not user:
            return {"message": gettext("user_not_found")}, 404

        try:
            confirmation = user.most_recent_confirmation
            print(confirmation.to_json())
            if confirmation:
                if confirmation.confirmed:
                    return {"message": gettext("confirmation_already_confirmed")}, 400
                confirmation.force_to_expire()
            print(confirmation.to_json())
            
            expire_at = int(time()) + CONFIRMATION_EXPIRATION_DELTA
            new_confirmation = ConfirmationModel(
                uid=uuid4().hex,
                expire_at=expire_at,
                confirmed=False,
                expired=False
            )
            user.confirmation.append(new_confirmation)
            user.save_to_db()
            user.send_confirmation_email()
            return {"message": gettext("confirmation_resend_successful")}, 201
        except MailgunException as e:
            return {"message": str(e)}, 500
        except:
            traceback.print_exc()
            return {"message": gettext("confirmation_resend_fail")}, 500