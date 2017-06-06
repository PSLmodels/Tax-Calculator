import requests
import time
from celery_status_server import server_url
def test_celery_status_server():
    tickets = []
    for repeat in range(4):
        ticket_id = requests.get('{0}/example_async'.format(server_url)).json().get('ticket_id','')
        register = requests.get('{0}/register_job?ticket_id={1}&email={2}&callback=google.com'.format(server_url,
                                                                                  ticket_id,
                                                                                  'email.com'))
        time.sleep(1)
        tickets.append(ticket_id)
    running = requests.get('{0}/celery_status_server'.format(server_url))
    print("ticket_id", ticket_id)
    try:
        running = running.json()
        print('running', running)
    except Exception as e:
        print(running._content)
        print('the above failed to .json() with ', e)
        raise
    for ticket_id in tickets:
        assert ticket_id in running
        assert 'inputs' in running[ticket_id]
        assert 'status' in running[ticket_id]
        assert 'eta' in running[ticket_id]
        assert 'email' in running[ticket_id]['inputs']
        assert 'started' in running[ticket_id]['inputs']
        assert running[ticket_id]['inputs']['email'] == 'email.com'
if __name__ == "__main__":
    test_celery_status_server()