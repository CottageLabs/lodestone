from service.lib.sword_thesis_deposit import SwordThesisDeposit
from service.lib.zendesk_tickets import ZendeskTickets
from redis import Redis
from octopus.core import app
from time import sleep
import traceback
from octopus.lib import mail
import sword2
from service import models

DEPOSIT_ERROR_MSG = """
There was an error attempting to deposit a thesis with job_id {x}.  The message from the SWORDv2 deposit
code was:

{y}

You should review the appropriate error queue in Redis to determine the cause of the error.
"""

TICKET_ERROR_MSG = """
There was an error attempting to make a zendesk ticket for job_id {x}.  The message from the
code was:

{y}

You should review the appropriate error queue in Redis to determine the cause of the error.
"""

def process_theses():
    r = Redis(host=app.config.get('REDIS_HOST'))
    deposit_queue = app.config.get('ETHESIS_SUBMIT_QUEUE')

    while True:
        while r.llen(deposit_queue) > 0:
            job_id = r.rpop(deposit_queue)
            if not job_id:
                sleep(2)
                continue
            deposited = _do_deposit(r, job_id)
            if deposited:
                _do_ticket(r, job_id)
            sleep(2)
        sleep(60)

def _do_deposit(r, job_id):
    poll_queue = app.config.get('ETHESIS_POLL_QUEUE')
    try:
        print '-' * 60
        print "Staring sword submission for %s" % job_id
        sword_deposit = SwordThesisDeposit(job_id)
        print "Preparing deposit"
        sword_deposit.prepare_deposit()
        print "Submitting deposit"
        if sword_deposit.deposit_thesis():
            print "Deposit successful"
            r.lpush(poll_queue, job_id)
            try:
                _send_confirmation(job_id)
            except:
                print "Sending confirmation email failed"
            return True
        else:
            print "Deposit failed."
            _record_deposit_error(r, job_id, "Deposit failed for unknown reason")
            return False
    except sword2.HTTPResponseError as e:
        msg = '!!!!!!!!!!!!!!!!!! SWORD Exception occured !!!!!!!!!!!!!!!!!!!!!!!!!!\n'
        msg += traceback.format_exc() + "\n"
        if e.response is not None:
            msg += "status " + str(e.response.status) + "\n"
        if e.content is not None:
            msg += e.content + "\n"
        print msg
        _record_deposit_error(r, job_id, msg)
        return False
    except Exception as e:
        msg = '!!!!!!!!!!!!!!!!!! General Exception occured !!!!!!!!!!!!!!!!!!!!!!!!!!\n'
        msg += traceback.format_exc() + "\n"
        print msg
        _record_deposit_error(r, job_id, msg)
        return False

def _do_ticket(r, job_id):
    try:
        print '-' * 60
        print "Creating ticket in Zendesk"
        z = ZendeskTickets('ethesis', job_id)
        ans = z.create_ethesis_ticket()
        if not ans:
            print "Ticket creation failed"
            _record_ticket_error(r, job_id, "Ticket creation failed")
    except:
        msg = '!!!!!!!!!!!!!!!!!! Zendesk Exception occured !!!!!!!!!!!!!!!!!!!!!!!!!!\n'
        msg += traceback.format_exc() + "\n"
        print msg
        _record_ticket_error(r, job_id, msg)

def _record_ticket_error(r, job_id, msg):
    deposit_queue = app.config.get('ETHESIS_SUBMIT_QUEUE')
    error_queue = "%s_error" % deposit_queue
    r.lpush(error_queue, job_id)

    to = app.config.get("DEPOSIT_ERROR_EMAIL")
    if to:
        mail.send_mail([to], "Zendesk Error", msg_body=TICKET_ERROR_MSG.format(x=job_id, y=msg))

def _record_deposit_error(r, job_id, msg):
    deposit_queue = app.config.get('ETHESIS_SUBMIT_QUEUE')
    error_queue = "%s_error" % deposit_queue
    r.lpush(error_queue, job_id)

    to = app.config.get("DEPOSIT_ERROR_EMAIL")
    if to:
        mail.send_mail([to], "Thesis Deposit Error", msg_body=DEPOSIT_ERROR_MSG.format(x=job_id, y=msg))

def _send_confirmation(job_id):
    record = models.Ethesis.pull(job_id)

    to = None
    subject = None
    body = None

    # get the best "to" address
    crsid = record.crsid
    if crsid is not None:
        to = crsid + "@xxxxxxx.ac.uk"
    if to is None:
        to = record.external_email
    if to is None:
        to = record.user_email

    first_name = record.given_names.split(" ")[0]
    title = record.title

    subject = app.config.get("ETHESIS_CONFIRM_SUBJECT", "")
    body_template = app.config.get("ETHESIS_CONFIRM_BODY", "")
    body = body_template.format(firstname=first_name, title=title)

    if to is not None:
        mail.send_mail([to], subject, msg_body=body)

if __name__ == '__main__':
    process_theses()
