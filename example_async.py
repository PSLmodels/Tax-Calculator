import os
import time
import json
from celery import Celery

celery_app = Celery('tasks3', broker=os.environ['REDISGREEN_URL'],
                backend=os.environ['REDISGREEN_URL'])

@celery_app.task
def example_async():

    time.sleep(30)
    return json.dumps({'example': 'ok'})
