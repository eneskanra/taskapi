import os
import time
import json
from datetime import datetime
from flask import request
from requests import Response
from celery import Celery
from mongoengine import connect
from libs.mailgun import Mailgun

#Specify mongodb host and database to connect to
MONGO_URI = 'mongodb://'+os.environ['MONGODB_USERNAME']+':'+os.environ['MONGODB_PASSWORD']+'@'+os.environ['MONGODB_HOSTNAME']+':27017/'+os.environ['MONGODB_DATABASE']
BROKER_URL = MONGO_URI

celery = Celery('EOD_TASKS',broker=BROKER_URL)

#Loads settings for Backend to store results of jobs 
celery.config_from_object('celeryconfig')

def send_task_reminder_email(email: str, task: str) -> Response:
        subject = "Task Reminder"
        text = f"You have a delayed task: {task}. Please change its status."
        html = f'<html>You have a delayed task: {task}. Please change its status.</html>'
        return Mailgun.send_email([email], subject, text, html)

@celery.task
def send_reminder_email():
    now = datetime.now()
    client = connect(host=MONGO_URI)
    db = client['flaskdb']
    projects = db.project_model.find({ "$or": [{"task.status": "Alındı"}, {"task.status":"Boşta"}]})
    print(projects.count())
    for project in projects:
        for task in project['task']:
            if task['status'] in ['Boşta', 'Alındı']:
                if "startdate" in task:
                    if now>task["startdate"]:
                        print(project['name']+"-"+task['title']+"-"+task['status']+"-"+str(task['startdate'])+"-"+str(task['owner']))
                        user = db.user_model.find({ "_id": project["owner"]})
                        for item in user:
                            print(item['email'])
                            send_task_reminder_email(item['email'], task['title'])
                            time.sleep(7)
    
    return {'message': "Mail başarıyla gönderildi"}, 200
