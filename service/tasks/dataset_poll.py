from service.lib.sword_data_deposit import SwordDataDeposit
from redis import Redis
from octopus.core import app
from time import sleep
from octopus.lib import mail
import traceback
from service.lib.zendesk_tickets import ZendeskTickets
import sword2

ERROR_MSG = """
There was an error attempting to poll DSpace for a dataset with job_id {x}.  The message from the SWORDv2
code was:

{y}

You should review the appropriate error queue in Redis to determine the cause of the error.
"""

def poll_datasets():
    r = Redis(host=app.config.get('REDIS_HOST'))
    poll_queue = app.config.get('DATASET_POLL_QUEUE')
    wait_queue = poll_queue + "_wait"
    poll_frequency = app.config.get("POLL_FREQUENCY", 86400)

    while True:
        # clear the poll queue
        while r.llen(poll_queue) > 0:
            job_id = r.rpop(poll_queue)
            if not job_id:
                sleep(2)
                continue
            _do_poll(r, job_id)
            sleep(2)

        # copy the contents of the wait queue to the poll queue
        print "requeueing polls to be done again..."
        while r.llen(wait_queue) > 0:
            job_id = r.rpop(wait_queue)
            r.lrem(poll_queue, job_id, 1)
            r.lpush(poll_queue, job_id)

        print "waiting for time to next run"
        sleep(poll_frequency)

def _do_poll(r, job_id):
    poll_queue = app.config.get('DATASET_POLL_QUEUE')
    wait_queue = poll_queue + "_wait"
    try:
        print '-' * 60
        print "Polling sword submission for %s" % job_id
        sword_deposit = SwordDataDeposit(job_id)
        ans = sword_deposit.poll_deposit()
        if ans == 'Error':
            print 'There was an error polling'
            _record_error(r, job_id, "No Edit IRI in record")
        elif not ans:
            print 'polling again later - state not archived'
            r.lpush(wait_queue, job_id)
        else:
            print 'job archived'
    except sword2.HTTPResponseError as e:
        msg = '!!!!!!!!!!!!!!!!!! SWORD Exception occured !!!!!!!!!!!!!!!!!!!!!!!!!!\n'
        msg += traceback.format_exc() + "\n"
        if e.response is not None:
            msg += "status " + str(e.response.status) + "\n"
        if e.content is not None:
            msg += e.content + "\n"
        print msg
        _record_error(r, job_id, msg)
    except Exception as e:
        msg = '!!!!!!!!!!!!!!!!!! General Exception occured !!!!!!!!!!!!!!!!!!!!!!!!!!\n'
        msg += traceback.format_exc() + "\n"
        print msg
        _record_error(r, job_id, msg)

    try:
        print '-' * 60
        print "Updating ticket in Zendesk if necessary"
        z = ZendeskTickets('dataset', job_id)
        ans = z.update_dataset_ticket()
        if not ans:
            msg = "Ticket update failed for unknown reason"
            _record_error(r, job_id, msg)
    except:
        msg = '!!!!!!!!!!!!!!!!!! Zendesk Exception occured !!!!!!!!!!!!!!!!!!!!!!!!!!\n'
        msg += traceback.format_exc() + "\n"
        print msg
        _record_error(r, job_id, msg)

def _record_error(r, job_id, msg):
    poll_queue = app.config.get('DATASET_POLL_QUEUE')
    error_queue = "%s_error" % poll_queue
    r.lpush(error_queue, job_id)

    to = app.config.get("DEPOSIT_ERROR_EMAIL")
    if to:
        mail.send_mail([to], "Dataset Poll Error", msg_body=ERROR_MSG.format(x=job_id, y=msg))

if __name__ == '__main__':
    poll_datasets()