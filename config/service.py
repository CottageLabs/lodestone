from octopus.lib import paths

##################################################
# overrides for the webapp deployment

DEBUG = True
PORT = 5000
SSL = False
THREADED = True

############################################
# important overrides for the ES module

# elasticsearch back-end connection settings
ELASTIC_SEARCH_HOST = "http://localhost:9200"
ELASTIC_SEARCH_INDEX = "lodestone"
ELASTIC_SEARCH_VERSION = "1.7.5"

############################################
# important overrides for account module

ACCOUNT_ENABLE = False

#############################################
# important overrides for storage module

# STORE_IMPL = "octopus.modules.store.store.StoreLocal"
# STORE_TMP_IMPL = "octopus.modules.store.store.TempStore"

STORE_LOCAL_DIR = paths.rel2abs(__file__, "..", "service", "tests", "local_store", "live")
STORE_TMP_DIR = paths.rel2abs(__file__, "..", "service", "tests", "local_store", "tmp")


##############################################
## Lodestone specific configuration

DEPOSIT_ERROR_EMAIL = False     # enter a suitable email address
MAIL_FROM_ADDRESS = "none@example.com"
MAIL_SUBJECT_PREFIX = "[lodestone] "
MAIL_SERVER = None          # default localhost
MAIL_PORT = 25              # default 25
#MAIL_USE_TLS               # default False
#MAIL_USE_SSL               # default False
#MAIL_DEBUG                 # default app.debug
#MAIL_USERNAME              # default None
#MAIL_PASSWORD              # default None
#MAIL_DEFAULT_SENDER        # default None
#MAIL_MAX_EMAILS            # default None
#MAIL_SUPPRESS_SEND         # default app.testing


REDIS_STATUS_DIR = 'tmp/data/redis_status_reports'

POLL_FREQUENCY = 86400

DEPOSIT_TIMEOUT = 300
HTTP_RETRY_ON_TIMEOUT = False
HTTP_RETRY_CODES = [
    409,    # conflict; not clear whether retry will help or not, but worth a go
    502,    # bad gateway; retry to see if the gateway can re-establish connection
    503,    # service unavailable; retry to see if it comes back
    504     # gateway timeout; retry to see if it responds next time
]

ETHESIS_UPLOAD_DIR = 'tmp/data/etheses'
ETHESIS_MULTIVALUED_FIELDS = ['authors', 'supervisors', 'keywords', 'other_languages']
# Error queues will have _error added to the end
ETHESIS_SUBMIT_QUEUE = 'ethesis_deposit'
ETHESIS_POLL_QUEUE = 'ethesis_poll'
ETHESIS_CONFIRM_SUBJECT = "Thank you for uploading your dissertation - we have received your submission."
ETHESIS_CONFIRM_BODY = """
Dear {firstname},

Thank you very much for submitting your thesis {title} to the repository. You will receive an email confirming the approval of your upload and containing the DOI link address in due course.

If you have any questions about your thesis submission please e-mail support@xxxxxxxx.ac.uk

With best wishes,

Repository support team
"""


DATASET_UPLOAD_DIR = 'tmp/data/datasets'
DATASET_MULTIVALUED_FIELDS = ['authors', 'keywords', 'resources', 'funders']
# Error queues will have _error added to the end
DATASET_SUBMIT_QUEUE = 'dataset_deposit'
DATASET_POLL_QUEUE = 'dataset_poll'
DATASET_CONFIRM_SUBJECT = "Thank you for submitting your research data to us - we have received your submission."

DATASET_CONFIRM_BODY_PLACEHOLDER = """
Dear {firstname},

Thank you very much for submitting your placeholder record for {title} to the repository. You will receive a placeholder DOI link for your placeholder record shortly. Please note that the placeholder DOI link will not resolve until we have reviewed and approved your data submission (up to three working days). We will email you after we have reviewed and approved your data submission.

To submit the final dataset files to us, please go to www.xxxxxxxxxx.ac.uk/upload and select the option "Modify a dataset". The placeholder DOI link address will not change after the final data files are added, so you may now use that DOI in your manuscript or any other places where you wish to provide a reference to your data files.

If you have any questions about your data submission please e-mail info@xxxxxxxxx.ac.uk

With best wishes,

Research Data Team
"""

DATASET_CONFIRM_BODY_FINAL = """
Dear {firstname},

Thank you very much for submitting {title} to the repository. You will receive a placeholder DOI link for your research data shortly. Please note that the placeholder DOI link will not resolve until we have reviewed and approved your data submission (up to three working days). We will email you after we have reviewed and approved your data submission.

If you have any questions about your data submission please e-mail info@xxxxxxxxx.ac.uk

With best wishes,

Research Data Team
"""

SWORD_DEPOSIT_DIR = 'tmp/data/sword_deposits'
SWORD_USERNAME = "sword_username"
SWORD_PASSWORD = "sword_password"
SWORD_ETHESIS_COLLECTION_IRI = "http://localhost:8080/swordv2/collection/123456789/2"
SWORD_DATASET_COLLECTION_IRI = "http://localhost:8080/swordv2/collection/123456789/12"

# If you provide a ZENDESK_TOKEN, this will be used instead of the ZENDESK_PASSWORD
ZENDESK_URL = 'https://zendesk/url/here'
ZENDESK_USERNAME = 'zendesk_username'
ZENDESK_PASSWORD = 'zendesk_password'
ZENDESK_TOKEN = None
ZENDESK_TICKET_REQUESTER_NAME = 'Requester name'
ZENDESK_TICKET_REQUESTER_EMAIL = 'Requester email'

# Default fields are the Production fields
# You should set this correctly in your local.cfg
# See template.local.cfg for examples of sandbox and production configuration
ZENDESK_DATA_FORM_FIELDS = {
    'ticket_form_id': 0,
    'ticket_type': 0,
    'ticket_priority': 0,
    'ticket_group_id': 0,
    'field_confidential_information': 0,
    'field_doi': 0,
    'field_supporting_publication': 0,
    'field_manuscript_title': 0,
    'field_journal_title': 0,
    'field_publication_date': 0,
    'field_article_link': 0,
    'field_published': 0,
    'field_accessible_to_peerreviewers': 0,
    'field_dataset_embargoed': 0,
    'field_promote_on_twitter': 0,
    'field_twitter_handle': 0,
    'field_additional_information': 0,
    'field_external_id': 0,
    'field_placeholder_dataset': 0,
    'field_title' : 0
}

# Default fields are the Production fields
# You should set this correctly in your local.cfg
# See template.local.cfg for examples of sandbox and production configuration
ZENDESK_THESIS_FORM_FIELDS = {
    'ticket_form_id': 0,
    'ticket_group_id': 0,
    'field_external_id': 0,
    'field_crsid': 0,
    'field_external_email_address': 0,
    'field_awarding_institution': 0,
    'field_college': 0,
    'field_department': 0,
    'field_qualification_level': 0,
    'field_degree': 0,
    'field_degree_title': 0,
    'field_thesis_title': 0,
    'field_date_awarded': 0,
    'field_funders': 0,
    'field_thesis_access_level': 0,
    'field_licence': 0
}

REDIS_HOST = 'localhost'

#######################################################
# Task scheduler configuration
#
SCHEDULER_TASKS = [
    # every 2 minutes trigger the task to process submitted theses and dataset records
    #       and create zendesk tickets for them
    # It is a long running task and should already be running.
    # This will hopefully start it if it has died or is not running
    # (2, "minutes", None, "service.tasks.ethesis_deposit.process_theses"),
    # (2, "minutes", None, "service.tasks.dataset_deposit.process_datasets"),
    # (2, "minutes", None, "service.tasks.ethesis_ticket_create.create_theses_ticket"),
    # (2, "minutes", None, "service.tasks.dataset_ticket_create.create_datasets_ticket"),

    # every 6 hours trigger the task to poll for updates to theses and dataset records
    # It is not a long running task but depends on the number of submissions to poll for updates.
    # This will check for updates every 6 hours
    # (6, "hours", None, "service.tasks.ethesis_poll.poll_theses"),
    # (6, "hours", None, "service.tasks.dataset_poll.poll_datasets"),
]
