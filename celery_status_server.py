#celery_status_server.py

from flask import Flask, request, make_response
from celery import Celery
from celery.app.control import Inspect
import datetime
import requests
import os
import json
import time
import sys
import subprocess as sp
from functools import partial
import example_async
"""
nohup redis-server &
nohup celery -A example_async worker -P eventlet -l info &
"""
server_app = Flask('celery_status_server')
port = 5070
server_url = "http://localhost:{0}".format(port)

TICKET_IDS_WATCHED = {}
m = '--module'
if not m in sys.argv:
    raise ValueError('needs --module that has the celery_app importable from here')
else:
    celery_app = __import__(sys.argv[sys.argv.index(m) + 1]).__dict__['celery_app']

def inspect_celery():
    global TICKET_IDS_WATCHED
    return_val = {}
    to_pop = []
    i = celery_app.control.inspect()
    print('i',i)
    for label, worker_check in zip(('active', 'scheduled'),(i.active(), i.scheduled())):
        print('worker_check', worker_check)
        if worker_check:
            for worker_id, worker_dict_list in worker_check.items():

                for worker_dict in worker_dict_list:
                    request = worker_dict.get('request', {})
                    job_id = worker_dict.get('id', request.get('id', None))
                    eta = worker_dict.get('eta', None)
                    if job_id in TICKET_IDS_WATCHED:
                        return_val[worker_dict['id']] = {'inputs': TICKET_IDS_WATCHED[job_id].copy(),
                                                         'status': label,
                                                         'eta': eta,
                                                         }
                    else:
                        pass
    for key in TICKET_IDS_WATCHED:
        if key not in return_val:
            return_val[key] = {'inputs': TICKET_IDS_WATCHED[key].copy(),
                               'status': 'done'}
            to_pop.append(key)
    response = {}
    for key in to_pop:
        worker_dict = TICKET_IDS_WATCHED.pop(key)
        if 'callback' in worker_dict:
            worker_dict['id'] = key
            callback = worker_dict['callback']
            if not callback.startswith('http://'):
                callback = 'http://' + callback
            worker_dict['callback'] = callback
            response = requests.post(callback, data=worker_dict)
            try:
                response = response.json()
            except Exception as e:
                print(response._content)
                print('failed to .json() the above')
                raise
        return_val[key] = {'callback_response': response}
    return return_val

@server_app.route('/example_async', methods=['GET'])
def example():

    ticket_id =  example_async.example_async.delay()
    print('ticket_id', ticket_id)
    url = '{0}/register_job?email={1}&ticket_id={2}&callback="http://google.com"'.format(server_url, ticket_id, ticket_id)
    return json.dumps({'ticket_id': str(ticket_id)})

@server_app.route("/register_job", methods=['GET'])
def register_job():
    print('hit register_job')
    global TICKET_IDS_WATCHED
    if not request.args.get('email', False) and not request.args.get('ticket_id', False):
        return make_response(json.dumps({'error': "Expected keys of email and ticket_id"}), 400)
    ticket_id = request.args['ticket_id']
    email = request.args['email']
    print("Start checking: {} with email {}".format(ticket_id, email))

    TICKET_IDS_WATCHED[ticket_id] = {'email': email,
                                     'started': datetime.datetime.utcnow().isoformat()}
    return json.dumps(inspect_celery())

@server_app.route("/celery_status_server", methods=['GET'])
def celery_status_server():
    print("results here")
    ticket_id = request.args.get('ticket_id','')
    if ticket_id:
        return json.dumps({ticket_id: inspect_celery().get('ticket_id')})
    return json.dumps(inspect_celery())



if __name__ == "__main__":
    server_app.debug = True
    server_app.run(host='localhost', port=port)
