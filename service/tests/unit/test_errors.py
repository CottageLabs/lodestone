from octopus.modules.es.testindex import ESTestCase
from service import models
import os, shutil
from service.tests import fixtures
from redis import Redis
from octopus.core import app
from service.tasks import ethesis_deposit, purge_tasks, ethesis_poll, dataset_deposit, dataset_poll
from service import deposit
from service.lib.crud_helper import CrudHelper
from service.lib import zendesk_tickets

def mock_deposit_none(*args, **kwargs):
    return None

def mock_deposit_raise(*args, **kwargs):
    raise RuntimeError("An error")

def mock_create_ticket_false(*args, **kwargs):
    return False

def mock_create_ticket_raise(*args, **kwargs):
    raise RuntimeError("An error")

def mock_poll(*args, **kwargs):
    raise RuntimeError("An error")

class TestModels(ESTestCase):
    def setUp(self):
        super(TestModels, self).setUp()
        self.old_deposit = deposit.deposit
        self.old_et_create = zendesk_tickets.ZendeskTickets.create_ethesis_ticket
        self.old_poll = deposit.poll
        if os.path.exists("tmp"):
            shutil.rmtree("tmp")

    def tearDown(self):
        super(TestModels, self).tearDown()
        deposit.deposit = self.old_deposit
        deposit.poll = self.old_poll
        zendesk_tickets.ZendeskTickets.create_ethesis_ticket = self.old_et_create

    def test_01_thesis_error_none(self):
        deposit.deposit = mock_deposit_none

        THESIS = fixtures.ThesisFixtureFactory.thesis()
        job_id = THESIS["id"]
        et = models.Ethesis(THESIS)
        et.save(blocking=True)

        r = Redis(host=app.config.get('REDIS_HOST'))
        ethesis_deposit._do_deposit(r, job_id)

    def test_02_thesis_error_raise(self):
        deposit.deposit = mock_deposit_raise

        THESIS = fixtures.ThesisFixtureFactory.thesis()
        job_id = THESIS["id"]
        et = models.Ethesis(THESIS)
        et.save(blocking=True)

        r = Redis(host=app.config.get('REDIS_HOST'))
        ethesis_deposit._do_deposit(r, job_id)

    def test_03_thesis_purge(self):
        deposit.deposit = mock_deposit_none

        # get our fixtures
        THESIS = fixtures.ThesisFixtureFactory.thesis()
        source_file = fixtures.ThesisFixtureFactory.pdf_path()

        # make an instance of the ethesis object
        job_id = THESIS["id"]
        et = models.Ethesis(THESIS)
        et.save(blocking=True)

        # copy in our test file
        os.makedirs(et.dir)
        shutil.copy(source_file, et.dir)

        ch = CrudHelper("ethesis", job_id)
        ch.submit_record()

        pt = purge_tasks.PurgeTasks("ethesis")
        pt.job(job_id)

    def test_04_thesis_zendesk_error_false(self):
        zendesk_tickets.ZendeskTickets.create_ethesis_ticket = mock_create_ticket_false

        THESIS = fixtures.ThesisFixtureFactory.thesis()
        job_id = THESIS["id"]
        et = models.Ethesis(THESIS)
        et.save(blocking=True)

        r = Redis(host=app.config.get('REDIS_HOST'))
        ethesis_deposit._do_ticket(r, job_id)

    def test_05_thesis_zendesk_error_raise(self):
        zendesk_tickets.ZendeskTickets.create_ethesis_ticket = mock_create_ticket_raise

        THESIS = fixtures.ThesisFixtureFactory.thesis()
        job_id = THESIS["id"]
        et = models.Ethesis(THESIS)
        et.save(blocking=True)

        r = Redis(host=app.config.get('REDIS_HOST'))
        ethesis_deposit._do_ticket(r, job_id)

    def test_06_thesis_poll_error_raise(self):
        deposit.poll = mock_poll

        THESIS = fixtures.ThesisFixtureFactory.thesis()
        job_id = THESIS["id"]
        THESIS["edit_iri"] = "http://whatever/"
        et = models.Ethesis(THESIS)
        et.save(blocking=True)

        r = Redis(host=app.config.get('REDIS_HOST'))
        ethesis_poll._do_poll(r, job_id)

    def test_07_data_error_none(self):
        deposit.deposit = mock_deposit_none

        DATASET = fixtures.DatasetFixtureFactory.dataset()
        job_id = DATASET["id"]
        ds = models.Dataset(DATASET)
        ds.save(blocking=True)

        r = Redis(host=app.config.get('REDIS_HOST'))
        dataset_deposit._do_deposit(r, job_id)

    def test_08_data_error_raise(self):
        deposit.deposit = mock_deposit_raise

        DATASET = fixtures.DatasetFixtureFactory.dataset()
        job_id = DATASET["id"]
        ds = models.Dataset(DATASET)
        ds.save(blocking=True)

        r = Redis(host=app.config.get('REDIS_HOST'))
        dataset_deposit._do_deposit(r, job_id)

    def test_09_data_purge(self):
        deposit.deposit = mock_deposit_none

        # get our fixtures
        DATASET = fixtures.DatasetFixtureFactory.dataset()
        source_file = fixtures.DatasetFixtureFactory.pdf_path()

        # make an instance of the ethesis object
        job_id = DATASET["id"]
        ds = models.Dataset(DATASET)
        ds.save(blocking=True)

        # copy in our test file
        os.makedirs(ds.dir)
        shutil.copy(source_file, ds.dir)

        ch = CrudHelper("dataset", job_id)
        ch.submit_record()

        pt = purge_tasks.PurgeTasks("dataset")
        pt.job(job_id)

    def test_10_data_zendesk_error_false(self):
        zendesk_tickets.ZendeskTickets.create_dataset_ticket = mock_create_ticket_false

        DATASET = fixtures.DatasetFixtureFactory.dataset()
        job_id = DATASET["id"]
        ds = models.Dataset(DATASET)
        ds.save(blocking=True)

        r = Redis(host=app.config.get('REDIS_HOST'))
        dataset_deposit._do_ticket(r, job_id)

    def test_11_data_zendesk_error_raise(self):
        zendesk_tickets.ZendeskTickets.create_dataset_ticket = mock_create_ticket_raise

        DATASET = fixtures.DatasetFixtureFactory.dataset()
        job_id = DATASET["id"]
        ds = models.Dataset(DATASET)
        ds.save(blocking=True)

        r = Redis(host=app.config.get('REDIS_HOST'))
        dataset_deposit._do_ticket(r, job_id)

    def test_12_data_poll_error_raise(self):
        deposit.poll = mock_poll

        DATASET = fixtures.DatasetFixtureFactory.dataset()
        job_id = DATASET["id"]
        DATASET["edit_iri"] = "http://whatever/"
        ds = models.Dataset(DATASET)
        ds.save(blocking=True)

        r = Redis(host=app.config.get('REDIS_HOST'))
        dataset_poll._do_poll(r, job_id)