from service.lib.zendesk_tickets import ZendeskTickets
from redis import Redis
from octopus.core import app
from time import sleep
import traceback
import sys
from octopus.lib import mail

ERROR_MSG = """
There was an error attempting to make a zendesk ticket for job_id {x}.  The message from the
code was:

{y}

You should review the appropriate error queue in Redis to determine the cause of the error.
"""

def create_theses_ticket():
    r = Redis(host=app.config.get('REDIS_HOST'))
    ticket_create_queue = app.config.get('ETHESIS_TICKET_CREATE_QUEUE')
    while r.llen(ticket_create_queue) > 0:
        job_id = r.rpop(ticket_create_queue)
        if not job_id:
            sleep(2)
            continue
        _do_ticket(r, job_id)
        sleep(2)
    sleep(60)

def _do_ticket(r, job_id):
    try:
        print '-' * 60
        print "Creating ticket in Zendesk"
        z = ZendeskTickets('ethesis', job_id)
        ans = z.create_ethesis_ticket()
        if not ans:
            print "Ticket creation failed"
            _record_error(r, job_id, "Ticket creation failed")
    except:
        print '!!!!!!!!!!!!!!!!!! Exception occured !!!!!!!!!!!!!!!!!!!!!!!!!!'
        traceback.print_exc(file=sys.stdout)
        _record_error(r, job_id, traceback.format_exc())

def _record_error(r, job_id, msg):
    ticket_create_queue = app.config.get('ETHESIS_TICKET_CREATE_QUEUE')
    error_queue = "%s_error" % ticket_create_queue
    r.lpush(error_queue, job_id)

    to = app.config.get("DEPOSIT_ERROR_EMAIL")
    if to:
        mail.send_mail([to], "Zendesk Error", msg_body=ERROR_MSG.format(x=job_id, y=msg))

if __name__ == '__main__':
    create_theses_ticket()