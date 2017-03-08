from octopus.modules.es.testindex import ESTestCase
from service.lib.sword_thesis_deposit import SwordThesisDeposit
from service.lib.sword_data_deposit import SwordDataDeposit
from service.lib.zendesk_tickets import ZendeskTickets
from service import models, deposit
import os, shutil, time
from service.tests import fixtures
from copy import deepcopy
from service.lib import helpers


UN = "richard@cottagelabs.com"
PW = "dspace"
COL_IRI = "http://localhost:8080/swordv2/collection/123456789/2"
MIMETYPE = "application/zip"
PACKAGING = "http://purl.org/net/sword/package/METSDSpaceSIP"
OBO = None

# we should be making our own payload from the fixture
# PAYLOAD = "/home/richard/Code/External/lodestone/python-client-sword2/tests/databank/example.zip"
PAYLOAD = "/home/richard/Code/External/lodestone/service/tests/resources/package.zip"

class TestModels(ESTestCase):
    def setUp(self):
        super(TestModels, self).setUp()
        if os.path.exists("tmp"):
            shutil.rmtree("tmp")

    def tearDown(self):
        super(TestModels, self).tearDown()

    def test_01_deposit_thesis_dspace(self):
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

        sword_deposit = SwordThesisDeposit(job_id)
        sword_deposit.prepare_deposit()
        payload = sword_deposit.zip_file

        edit_iri = deposit.deposit(payload, UN, PW, COL_IRI, OBO)
        print edit_iri

        receipt, states = deposit.poll(edit_iri, UN, PW)
        print states

        # sword_deposit.deposit_thesis()

    def test_02_thesis_zendesk(self):
        THESIS = fixtures.ThesisFixtureFactory.thesis()

        # make an instance of the ethesis object
        job_id = THESIS["id"]
        et = models.Ethesis(THESIS)
        et.save(blocking=True)

        z = ZendeskTickets('ethesis', job_id)
        ans = z.create_ethesis_ticket()
        print ans

    def test_03_blocking_poll_thesis_dspace(self):
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

        sword_deposit = SwordThesisDeposit(job_id)
        sword_deposit.prepare_deposit()
        payload = sword_deposit.zip_file

        edit_iri = deposit.deposit(payload, UN, PW, COL_IRI, OBO)
        print edit_iri

        state_uri = None
        states = None
        while state_uri != "http://dspace.org/state/archived":
            time.sleep(10)
            receipt, states = deposit.poll(edit_iri, UN, PW)
            state_uri, desc = states.states[0]
            print state_uri
        print state_uri

    def test_04_blocking_poll_thesis_update_files(self):
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

        sword_deposit = SwordThesisDeposit(job_id)
        sword_deposit.prepare_deposit()
        sword_deposit.deposit_thesis()

        status_code = None
        while status_code != "archived":
            time.sleep(10)
            sword_deposit.poll_deposit()
            status_code = sword_deposit.thesis_dao.status_code
            print status_code

    def test_05_dataset_zendesk(self):
        DATASET = fixtures.DatasetFixtureFactory.dataset()
        doi = DATASET["doi"]
        del DATASET["doi"]

        # make an instance of the ethesis object
        job_id = DATASET["id"]
        ds = models.Dataset(DATASET)
        ds.save(blocking=True)

        z = ZendeskTickets('dataset', job_id)
        ans = z.create_dataset_ticket()
        print ans

        assert z.dao.dao_record.ticket_id is not None

        z.dao.dao_record.doi = doi
        z.dao.dao_record.save(blocking=True)

        # have to re-initialise to re-load from the index
        z = ZendeskTickets('dataset', job_id)
        ans = z.update_dataset_ticket()
        print ans

    def test_06_deposit_dataset_dspace(self):
        # get our fixtures
        DATASET = fixtures.DatasetFixtureFactory.dataset()
        DATASET["iscitedby"] = "10.whatever"    # just to check it is identified correctly
        source_file = fixtures.DatasetFixtureFactory.pdf_path()

        # make an instance of the ethesis object
        job_id = DATASET["id"]
        ds = models.Dataset(DATASET)
        ds.save(blocking=True)

        # copy in our test file
        os.makedirs(ds.dir)
        shutil.copy(source_file, ds.dir)

        sword_deposit = SwordDataDeposit(job_id)
        sword_deposit.prepare_deposit()
        payload = sword_deposit.zip_file

        edit_iri = deposit.deposit(payload, UN, PW, COL_IRI, OBO)
        print edit_iri

        receipt, states = deposit.poll(edit_iri, UN, PW)
        print states

    def test_07_blocking_poll_data_dspace(self):
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

        sword_deposit = SwordDataDeposit(job_id)
        sword_deposit.prepare_deposit()
        payload = sword_deposit.zip_file

        edit_iri = deposit.deposit(payload, UN, PW, COL_IRI, OBO)
        print edit_iri

        state_uri = None
        states = None
        while state_uri != "http://dspace.org/state/archived":
            time.sleep(10)
            receipt, states = deposit.poll(edit_iri, UN, PW)
            state_uri, desc = states.states[0]
            print state_uri
        print state_uri

    def test_08_blocking_poll_data_update_files(self):
        # get our fixtures
        DATASET = fixtures.DatasetFixtureFactory.dataset()
        del DATASET["doi"]
        source_file = fixtures.DatasetFixtureFactory.pdf_path()

        # make an instance of the ethesis object
        job_id = DATASET["id"]
        ds = models.Dataset(DATASET)
        ds.save(blocking=True)

        # copy in our test file
        os.makedirs(ds.dir)
        shutil.copy(source_file, ds.dir)

        sword_deposit = SwordDataDeposit(job_id)
        sword_deposit.prepare_deposit()
        sword_deposit.deposit_dataset()

        status_code = None
        while status_code != "archived":
            time.sleep(10)
            sword_deposit.poll_deposit()
            status_code = sword_deposit.data_dao.status_code
            print status_code

    def test_09_big_dataset(self):
        # get our fixtures
        DATASET = fixtures.DatasetFixtureFactory.dataset()
        del DATASET["doi"]
        DATASET["files"] = []

        source_file = "/home/richard/Downloads/ideaIU-15.0.2.tar.gz"

        size = os.path.getsize(source_file)
        sha1 = helpers.get_sha1(source_file)
        file_entry = {
            "file_name": "pdf1.pdf",
            "file_url": "/data/ad8e6ab2-dc18-4b4f-aa14-5f7c2f148788/files/",
            "file_format": [
                "Format"
            ],
            "file_size": size,
            "file_fixity": {
                "type": "SHA1",
                "value": sha1
            },
            "file_mime_type": "application/pdf",
            "file_path": "tmp/data/datasets/ad/8e/6ab2-dc18-4b4f-aa14-5f7c2f148788/",
            "software": [
                "Software"
            ]
        }

        # make an instance of the ethesis object
        job_id = DATASET["id"]
        ds = models.Dataset(DATASET)
        ds.save(blocking=True)

        # copy in our test files to make the thing very very large
        os.makedirs(ds.dir)
        for i in range(10):
            fe = deepcopy(file_entry)
            fe["file_name"] = "file" + str(i) + ".dat"
            fe["file_url"] += fe["file_name"]
            fe["file_path"] += fe["file_name"]
            DATASET["files"].append(fe)

            shutil.copy(source_file, os.path.join(ds.dir, fe["file_name"]))


